import argparse
import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from generator.batch_state import BatchState
from generator.capture.exporter import export_sharegpt, load_trajectories
from generator.config import DATA_DIR, TRAJECTORIES_DIR, SHAREGPT_DIR, OUTPUT_DIR, MODEL_POOL
from generator.models.project import AnchorProject, ProjectType
from generator.pipeline import TrajectoryPipeline

console = Console()


def load_anchor_projects() -> dict[str, list[AnchorProject]]:
    projects = {"cli_tool": [], "python_package": [], "js_ts_package": []}

    mapping = {
        "cli_tools.json": ("cli_tool", ProjectType.CLI_TOOL),
        "python_packages.json": ("python_package", ProjectType.PYTHON_PACKAGE),
        "js_ts_packages.json": ("js_ts_package", ProjectType.JS_TS_PACKAGE),
    }

    for filename, (key, ptype) in mapping.items():
        fp = DATA_DIR / filename
        if not fp.exists():
            continue
        with open(fp) as f:
            data = json.load(f)
        for item in data:
            projects[key].append(AnchorProject(
                name=item["name"],
                repo=item["repo"],
                category=item["category"],
                language=item.get("language"),
                project_type=ptype,
            ))

    return projects


def find_project(name: str, project_type: str | None = None) -> AnchorProject | None:
    all_projects = load_anchor_projects()
    for ptype, plist in all_projects.items():
        if project_type and ptype != project_type:
            continue
        for p in plist:
            if p.name.lower() == name.lower():
                return p
    return None


def cmd_run(args):
    if args.repo:
        ptype = ProjectType(args.type) if args.type else ProjectType.PYTHON_PACKAGE
        project = AnchorProject(
            name=args.repo.split("/")[-1],
            repo=args.repo,
            category="custom",
            project_type=ptype,
        )
    elif args.project:
        project = find_project(args.project, args.type)
        if not project:
            console.print(f"[red]Project '{args.project}' not found in anchor list[/]")
            return
    else:
        console.print("[red]Must specify --project or --repo[/]")
        return

    roles = _parse_roles(args.models)

    output_dir = Path(args.output_dir) if args.output_dir else TRAJECTORIES_DIR

    pipeline = TrajectoryPipeline(
        roles=roles,
        output_dir=output_dir,
        verbose=args.verbose,
    )

    console.print(f"\n[bold]Context Learning Trajectory Generator[/]")
    console.print(f"Project: {project.name} ({project.repo})")
    console.print(f"Type: {project.project_type.value}")
    console.print(f"Roles: {pipeline.roles}\n")

    if args.all_requirements or args.num_requirements:
        asyncio.run(pipeline.run_project(
            project,
            concurrency=args.concurrency,
            max_requirements=args.num_requirements,
        ))
    else:
        asyncio.run(pipeline.run_single(project))


def cmd_export(args):
    input_path = Path(args.input) if args.input else TRAJECTORIES_DIR
    records = load_trajectories(input_path)

    if not records:
        console.print("[red]No trajectory records found[/]")
        return

    console.print(f"[green]Loaded {len(records)} trajectory records[/]")

    if args.format == "sharegpt":
        output_path = Path(args.output) if args.output else SHAREGPT_DIR / "export.json"
        export_sharegpt(records, output_path, quality_filter=not args.no_filter)
        console.print(f"[green]Exported to {output_path}[/]")
    else:
        console.print(f"[red]Unknown format: {args.format}[/]")


def _parse_roles(models_json: str | None) -> dict | None:
    if not models_json:
        return None
    try:
        overrides = json.loads(models_json)
        from generator.config import DEFAULT_ROLES
        roles = dict(DEFAULT_ROLES)
        for role, model_key in overrides.items():
            if model_key in MODEL_POOL:
                roles[role] = MODEL_POOL[model_key]
            else:
                roles[role] = model_key
        return roles
    except json.JSONDecodeError:
        console.print("[red]Invalid --models JSON[/]")
        return None


def cmd_batch(args):
    state = None
    state_file = getattr(args, 'state_file', None)
    if args.resume:
        state_path = Path(args.resume)
    elif state_file:
        state_path = Path(state_file)
    else:
        state_path = OUTPUT_DIR / "batch_state.json"

    if args.resume:
        state = BatchState.load(state_path)
        console.print(f"[bold]Resuming batch: {state.batch_id}[/]")
        console.print(f"[dim]{state.progress_str}[/]")
        project_type = state.project_type
        count = state.total_projects
        reqs = state.reqs_per_project
    else:
        project_type = args.type or "python_package"
        count = args.count
        reqs = args.reqs_per_project

    all_projects = load_anchor_projects()
    project_list = all_projects.get(project_type, [])

    if not project_list:
        console.print(f"[red]No projects found for type '{project_type}'[/]")
        return

    start = getattr(args, 'start', 0) or 0
    projects = project_list[start:start + count]

    roles = _parse_roles(args.models)

    pipeline = TrajectoryPipeline(
        roles=roles,
        output_dir=TRAJECTORIES_DIR,
        verbose=args.verbose,
    )

    coder_models = None
    coder_split = None
    if args.multi_coder:
        try:
            coder_models = json.loads(args.multi_coder)
        except json.JSONDecodeError:
            console.print("[red]Invalid --multi-coder JSON[/]")
            return
    if args.coder_split:
        coder_split = [int(x) for x in args.coder_split.split(",")]
        if sum(coder_split) != reqs:
            console.print(f"[red]--coder-split sum ({sum(coder_split)}) must equal --reqs-per-project ({reqs})[/]")
            return

    console.print(f"\n[bold]Context Learning Batch Generator[/]")
    console.print(f"Type: {project_type}")
    console.print(f"Projects: {len(projects)}")
    console.print(f"Reqs/project: {reqs}")
    console.print(f"Project concurrency: {args.project_concurrency}")
    console.print(f"Req concurrency: {args.req_concurrency}")
    console.print(f"Roles: {pipeline.roles}")
    if coder_models:
        console.print(f"Multi-coder: {coder_models} (split: {coder_split or 'round-robin'})")
    console.print()

    asyncio.run(pipeline.run_batch(
        projects=projects,
        reqs_per_project=reqs,
        project_concurrency=args.project_concurrency,
        req_concurrency=args.req_concurrency,
        state_path=state_path,
        state=state,
        coder_models=coder_models,
        coder_split=coder_split,
    ))


def cmd_list(args):
    all_projects = load_anchor_projects()

    table = Table(title="Anchor Projects")
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="green")

    for ptype, plist in all_projects.items():
        if args.type and ptype != args.type:
            continue
        filtered = plist
        if args.category:
            filtered = [p for p in plist if args.category.lower() in p.category.lower()]

        if args.show_all:
            for p in filtered[:50]:
                table.add_row(ptype, f"{p.name} ({p.repo}) [{p.category}]")
            if len(filtered) > 50:
                table.add_row(ptype, f"... and {len(filtered) - 50} more")
        else:
            table.add_row(ptype, str(len(filtered)))

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Context Learning Trajectory Generator",
    )
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run trajectory generation pipeline")
    run_parser.add_argument("--project", help="Project name from anchor list")
    run_parser.add_argument("--repo", help="Direct GitHub repo (owner/repo)")
    run_parser.add_argument("--type", choices=["cli_tool", "python_package", "js_ts_package"])
    run_parser.add_argument("--models", help='Model overrides JSON: \'{"coder": "gpt-5.2-codex"}\'')
    run_parser.add_argument("--output-dir", help="Output directory")
    run_parser.add_argument("--all-requirements", action="store_true", help="Process all generated requirements")
    run_parser.add_argument("-n", "--num-requirements", type=int, help="Number of requirements to process")
    run_parser.add_argument("-c", "--concurrency", type=int, default=1, help="Number of requirements to process in parallel")
    run_parser.add_argument("--verbose", "-v", action="store_true")
    run_parser.set_defaults(func=cmd_run)

    # export
    export_parser = subparsers.add_parser("export", help="Export trajectories")
    export_parser.add_argument("--input", help="Input JSONL file or directory")
    export_parser.add_argument("--format", default="sharegpt", choices=["sharegpt"])
    export_parser.add_argument("--output", "-o", help="Output file path")
    export_parser.add_argument("--no-filter", action="store_true", help="Include FAIL trajectories")
    export_parser.set_defaults(func=cmd_export)

    # batch
    batch_parser = subparsers.add_parser("batch", help="Batch process multiple projects")
    batch_parser.add_argument("--type", choices=["cli_tool", "python_package", "js_ts_package"], default="python_package")
    batch_parser.add_argument("--start", type=int, default=0, help="Start index in project list (for splitting)")
    batch_parser.add_argument("--count", type=int, default=200, help="Number of projects to process")
    batch_parser.add_argument("--reqs-per-project", type=int, default=5, help="Requirements per project")
    batch_parser.add_argument("--state-file", help="Custom batch state file path (for parallel batches)")
    batch_parser.add_argument("--project-concurrency", type=int, default=3, help="Projects to process in parallel")
    batch_parser.add_argument("--req-concurrency", type=int, default=5, help="Requirements per project in parallel")
    batch_parser.add_argument("--resume", help="Resume from batch state file")
    batch_parser.add_argument("--models", help='Model overrides JSON')
    batch_parser.add_argument("--multi-coder", help='JSON list of coder models: \'["z-ai/glm-5", "moonshotai/kimi-k2.5"]\'')
    batch_parser.add_argument("--coder-split", help='Comma-separated req counts per coder: "2,3"')
    batch_parser.add_argument("--verbose", "-v", action="store_true")
    batch_parser.set_defaults(func=cmd_batch)

    # list
    list_parser = subparsers.add_parser("list-projects", help="List anchor projects")
    list_parser.add_argument("--type", choices=["cli_tool", "python_package", "js_ts_package"])
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--show-all", action="store_true", help="Show project names")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
