import asyncio
import json
import signal
import uuid
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.table import Table

from generator.batch_state import BatchState, ProjectResult
from generator.capture.exporter import export_jsonl
from generator.capture.recorder import TrajectoryRecorder
from generator.config import DEFAULT_ROLES, MAX_CONVERSATION_TURNS, MAX_FIX_ATTEMPTS, TRAJECTORIES_DIR, OUTPUT_DIR

TOOL_LOOP_TIMEOUT = 600      # 10 minutes per tool calling loop
REQUIREMENT_TIMEOUT = 900    # 15 minutes per requirement
PROJECT_TIMEOUT = 3600       # 1 hour per project
from generator.llm.client import AsyncOpenRouterClient
from generator.models.project import AnchorProject
from generator.models.requirement import Requirement, RequirementSet
from generator.models.trajectory import TrajectoryRecord
from generator.project_access.cloner import clone_project
from generator.stages.analyzer import ProjectAnalyzer
from generator.stages.coder_agent import CoderAgent
from generator.stages.reviewer_agent import ReviewerAgent
from generator.stages.user_agent import UserAgent

console = Console()


class TrajectoryPipeline:
    def __init__(
        self,
        roles: dict[str, str] | None = None,
        output_dir: Path = TRAJECTORIES_DIR,
        verbose: bool = False,
    ):
        self.roles = roles or dict(DEFAULT_ROLES)
        self.output_dir = output_dir
        self.verbose = verbose

    async def run_single(
        self,
        project: AnchorProject,
        requirement: Requirement | None = None,
        coder_model: str | None = None,
    ) -> TrajectoryRecord:
        recorder = TrajectoryRecorder()
        client = AsyncOpenRouterClient(recorder=recorder)
        start_time = datetime.now(timezone.utc)

        try:
            # Clone project
            console.print(f"[bold blue]Cloning {project.repo}...[/]")
            project_root = await clone_project(project.repo)
            console.print(f"[green]Project cloned to {project_root}[/]")

            # Stage 1: Analyze project and generate requirements
            if requirement is None:
                console.print("[bold yellow]Stage 1: Analyzing project...[/]")
                recorder.start_stage("analyzer", 1, self.roles["analyzer"])
                analyzer = ProjectAnalyzer(client, self.roles["analyzer"])
                req_set = await analyzer.analyze(project, project_root)
                recorder.end_stage()

                if not req_set.requirements:
                    raise RuntimeError("No requirements generated")

                requirement = req_set.requirements[0]
                console.print(f"[green]Generated {len(req_set.requirements)} requirements[/]")
                console.print(f"[dim]Selected: {requirement.description}[/]")
            else:
                console.print("[dim]Using provided requirement, skipping Stage 1[/]")

            # Stage 2: User agent initiates conversation
            console.print("[bold yellow]Stage 2: User initiating conversation...[/]")
            recorder.start_stage("user_initiate", 2, self.roles["user"])
            user_agent = UserAgent(client, self.roles["user"])
            user_message = await user_agent.initiate_conversation(requirement, project)
            recorder.end_stage()

            if self.verbose:
                console.print(f"[dim]User: {user_message[:200]}...[/]")

            # Stage 3: Coder agent responds (multi-turn)
            actual_coder = coder_model or self.roles["coder"]
            console.print("[bold yellow]Stage 3: Coder agent working...[/]")
            recorder.start_stage("coder", 3, actual_coder)
            coder = CoderAgent(client, actual_coder)

            conversation_history = []
            script = None
            final_response = ""

            for turn in range(MAX_CONVERSATION_TURNS):
                console.print(f"[dim]  Turn {turn + 1}/{MAX_CONVERSATION_TURNS}[/]")
                response, extracted_script = await coder.respond(
                    user_message=user_message,
                    conversation_history=conversation_history,
                    project=project,
                    project_root=project_root,
                )

                final_response = response
                if extracted_script:
                    script = extracted_script

                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": response})

                if script:
                    break

                # User follow-up
                followup = await user_agent.generate_followup(requirement, response)
                if followup is None:
                    break
                user_message = followup
                if self.verbose:
                    console.print(f"[dim]  User follow-up: {followup[:100]}...[/]")

            recorder.end_stage()

            if not script:
                console.print("[red]No script generated by coder agent[/]")
                script = ""

            if self.verbose and script:
                console.print(f"[green]Script generated ({len(script)} chars)[/]")

            # Stage 4: Review → Fix loop
            reviewer = ReviewerAgent(client, self.roles["reviewer"])
            review = None

            for fix_round in range(MAX_FIX_ATTEMPTS + 1):
                # Review
                stage_label = "reviewer" if fix_round == 0 else f"reviewer_round{fix_round + 1}"
                stage_num = 4 + fix_round * 2
                console.print(f"[bold yellow]Stage {stage_num}: Reviewing script (round {fix_round + 1})...[/]")
                recorder.start_stage(stage_label, stage_num, self.roles["reviewer"])
                review = await reviewer.review(script, requirement, project, project_root)
                recorder.end_stage()

                console.print(f"[{'green' if review.verdict == 'PASS' else 'red'}]Review: {review.verdict}[/]")
                if self.verbose:
                    console.print(f"[dim]{review.reasoning}[/]")

                if review.verdict == "PASS" or fix_round == MAX_FIX_ATTEMPTS:
                    break

                # Fix
                fix_stage_num = stage_num + 1
                console.print(f"[bold yellow]Stage {fix_stage_num}: Fixing script (attempt {fix_round + 1})...[/]")
                recorder.start_stage(f"fixer_round{fix_round + 1}", fix_stage_num, self.roles["coder"])
                fix_response, fixed_script = await coder.fix(
                    script, requirement, review, project, project_root,
                )
                recorder.end_stage()

                if fixed_script:
                    script = fixed_script
                    console.print(f"[green]Script fixed ({len(script)} chars)[/]")
                else:
                    console.print("[red]Fix attempt produced no script, keeping original[/]")

            # User verification
            final_stage_num = 4 + (MAX_FIX_ATTEMPTS + 1) * 2
            console.print(f"[bold yellow]Stage {final_stage_num}: User verification...[/]")
            recorder.start_stage("user_verify", final_stage_num, self.roles["user"])
            verification = await user_agent.verify_script(requirement, script, review)
            recorder.end_stage()

            console.print(f"[{'green' if verification.verdict == 'PASS' else 'red'}]Verification: {verification.verdict} ({verification.requirement_coverage})[/]")

            # Build trajectory record
            final_quality = "PASS" if review.verdict == "PASS" and verification.verdict == "PASS" else "FAIL"

            record = TrajectoryRecord(
                trajectory_id=str(uuid.uuid4()),
                project=project,
                requirement=requirement,
                stages=recorder.stages,
                full_conversation=recorder.get_conversation_history(),
                generated_script=script or None,
                review_verdict=review.verdict,
                review_reasoning=review.reasoning,
                user_verification=verification.verdict,
                user_verification_reasoning=verification.reasoning,
                final_quality=final_quality,
                total_api_calls=recorder.total_api_calls,
                total_tokens=recorder.total_input_tokens + recorder.total_output_tokens,
                total_duration_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
                generated_at=datetime.now(timezone.utc).isoformat(),
            )

            # Save trajectory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"{project.name}__{requirement.id}__{ts}.jsonl"
            export_jsonl([record], output_file)
            console.print(f"\n[bold green]Trajectory saved to {output_file}[/]")
            console.print(f"[dim]Quality: {final_quality} | API calls: {record.total_api_calls} | Tokens: {record.total_tokens} | Duration: {record.total_duration_seconds:.1f}s[/]")

            return record

        finally:
            await client.close()

    def _assign_coders(
        self,
        num_reqs: int,
        coder_models: list[str] | None,
        coder_split: list[int] | None,
    ) -> list[str | None]:
        """Assign coder models to requirements based on split."""
        if not coder_models:
            return [None] * num_reqs

        if coder_split:
            assignments = []
            for model, count in zip(coder_models, coder_split):
                assignments.extend([model] * count)
            while len(assignments) < num_reqs:
                assignments.append(coder_models[-1])
            return assignments[:num_reqs]
        else:
            return [coder_models[i % len(coder_models)] for i in range(num_reqs)]

    async def run_project(
        self,
        project: AnchorProject,
        concurrency: int = 1,
        max_requirements: int | None = None,
        coder_models: list[str] | None = None,
        coder_split: list[int] | None = None,
    ) -> list[TrajectoryRecord]:
        recorder = TrajectoryRecorder()
        client = AsyncOpenRouterClient(recorder=recorder)

        try:
            project_root = await clone_project(project.repo)
            analyzer = ProjectAnalyzer(client, self.roles["analyzer"])
            req_set = await analyzer.analyze(project, project_root)
        finally:
            await client.close()

        requirements = req_set.requirements
        if max_requirements:
            requirements = requirements[:max_requirements]

        coder_assignments = self._assign_coders(len(requirements), coder_models, coder_split)

        console.print(f"\n[bold]Processing {len(requirements)} requirements (concurrency={concurrency})[/]")

        if concurrency <= 1:
            records = []
            for i, req in enumerate(requirements):
                console.print(f"\n[bold]Processing: {req.id} - {req.description[:80]}...[/]")
                try:
                    record = await asyncio.wait_for(
                        self.run_single(project, requirement=req, coder_model=coder_assignments[i]),
                        timeout=REQUIREMENT_TIMEOUT,
                    )
                    records.append(record)
                except asyncio.TimeoutError:
                    console.print(f"[red]Timed out on {req.id} (>{REQUIREMENT_TIMEOUT}s)[/]")
                except Exception as e:
                    console.print(f"[red]Failed on {req.id}: {e}[/]")
            return records

        semaphore = asyncio.Semaphore(concurrency)
        results: list[TrajectoryRecord | None] = [None] * len(requirements)

        async def _run_one(idx: int, req: Requirement):
            async with semaphore:
                console.print(f"\n[bold cyan][{idx+1}/{len(requirements)}] Starting: {req.id} - {req.description[:60]}...[/]")
                try:
                    record = await asyncio.wait_for(
                        self.run_single(project, requirement=req, coder_model=coder_assignments[idx]),
                        timeout=REQUIREMENT_TIMEOUT,
                    )
                    results[idx] = record
                except asyncio.TimeoutError:
                    console.print(f"[red][{idx+1}] Timed out {req.id} (>{REQUIREMENT_TIMEOUT}s)[/]")
                except Exception as e:
                    console.print(f"[red][{idx+1}] Failed {req.id}: {e}[/]")

        tasks = [_run_one(i, req) for i, req in enumerate(requirements)]
        await asyncio.gather(*tasks)

        records = [r for r in results if r is not None]
        console.print(f"\n[bold green]Completed: {len(records)}/{len(requirements)} requirements[/]")
        return records

    async def run_batch(
        self,
        projects: list[AnchorProject],
        reqs_per_project: int = 5,
        project_concurrency: int = 3,
        req_concurrency: int = 5,
        state_path: Path | None = None,
        state: BatchState | None = None,
        coder_models: list[str] | None = None,
        coder_split: list[int] | None = None,
    ) -> BatchState:
        state_path = state_path or (OUTPUT_DIR / "batch_state.json")

        if state is None:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            state = BatchState(
                batch_id=batch_id,
                total_projects=len(projects),
                reqs_per_project=reqs_per_project,
                project_type=projects[0].project_type.value if projects else "",
                pending=[p.name for p in projects],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )
            # Filter out already completed/failed from a potential stale pending list
            state.save(state_path)

        # On resume: retry failed projects (move them back to pending)
        if state.failed:
            retry_names = list(state.failed.keys())
            for name in retry_names:
                del state.failed[name]
                if name not in state.pending:
                    state.pending.append(name)
            state.save(state_path)
            console.print(f"[bold yellow]Retrying {len(retry_names)} previously failed projects[/]")

        # Filter projects to only pending ones (skip completed)
        done_names = set(state.completed.keys())
        pending_projects = [p for p in projects if p.name not in done_names]

        if not pending_projects:
            console.print("[bold green]All projects already processed![/]")
            return state

        console.print(f"\n[bold]Batch: {state.batch_id}[/]")
        console.print(f"[dim]{state.progress_str}[/]")
        console.print(f"[dim]Processing {len(pending_projects)} remaining projects (project_concurrency={project_concurrency}, req_concurrency={req_concurrency})[/]\n")

        # Graceful shutdown
        shutdown_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        def _signal_handler():
            if not shutdown_event.is_set():
                console.print("\n[bold red]Shutdown requested — finishing current projects...[/]")
                shutdown_event.set()

        try:
            loop.add_signal_handler(signal.SIGINT, _signal_handler)
        except NotImplementedError:
            pass  # Windows

        semaphore = asyncio.Semaphore(project_concurrency)
        lock = asyncio.Lock()

        def _make_progress_table() -> Table:
            table = Table(title=f"Batch Progress: {state.batch_id}", expand=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Completed", str(len(state.completed)))
            table.add_row("Failed", str(len(state.failed)))
            table.add_row("Pending", str(len(state.pending)))
            table.add_row("Total Trajectories", str(state.stats.total_trajectories))
            table.add_row("PASS / FAIL", f"{state.stats.total_pass} / {state.stats.total_fail}")
            table.add_row("Total Tokens", f"{state.stats.total_tokens:,}")
            return table

        async def _run_project(project: AnchorProject):
            if shutdown_event.is_set():
                return

            async with semaphore:
                if shutdown_event.is_set():
                    return

                idx = len(state.completed) + len(state.failed) + 1
                console.print(f"[bold cyan][{idx}/{state.total_projects}] Starting: {project.name} ({project.repo})[/]")

                try:
                    records = await asyncio.wait_for(
                        self.run_project(
                            project,
                            concurrency=req_concurrency,
                            max_requirements=reqs_per_project,
                            coder_models=coder_models,
                            coder_split=coder_split,
                        ),
                        timeout=PROJECT_TIMEOUT,
                    )

                    passed = sum(1 for r in records if r.final_quality == "PASS")
                    failed_count = len(records) - passed
                    tokens = sum(r.total_tokens for r in records)

                    result = ProjectResult(
                        trajectories=len(records),
                        passed=passed,
                        failed=failed_count,
                        tokens=tokens,
                    )

                    async with lock:
                        state.mark_completed(project.name, result)
                        state.save(state_path)

                    console.print(f"[bold green][{project.name}] Done: {passed} pass, {failed_count} fail, {tokens:,} tokens[/]")

                except asyncio.TimeoutError:
                    error_msg = f"Project timed out after {PROJECT_TIMEOUT}s"
                    async with lock:
                        state.mark_failed(project.name, error_msg)
                        state.save(state_path)
                    console.print(f"[bold red][{project.name}] Timed out: {error_msg}[/]")

                except Exception as e:
                    error_msg = f"{type(e).__name__}: {e}"
                    async with lock:
                        state.mark_failed(project.name, error_msg)
                        state.save(state_path)
                    console.print(f"[bold red][{project.name}] Failed: {error_msg}[/]")

        tasks = []
        for project in pending_projects:
            if shutdown_event.is_set():
                break
            tasks.append(_run_project(project))

        await asyncio.gather(*tasks, return_exceptions=True)

        # Final save
        state.save(state_path)

        # Summary
        console.print(f"\n[bold]{'='*60}[/]")
        console.print(f"[bold]Batch Complete: {state.batch_id}[/]")
        console.print(_make_progress_table())
        console.print(f"[dim]State saved to {state_path}[/]")

        try:
            loop.remove_signal_handler(signal.SIGINT)
        except (NotImplementedError, ValueError):
            pass

        return state
