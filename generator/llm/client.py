import asyncio
import json
import time
from datetime import datetime, timezone

import httpx

from generator.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    API_TIMEOUT_SECONDS,
    MAX_RETRIES,
    MAX_TOOL_ITERATIONS,
)
from generator.models.conversation import Message, ToolCallRecord


class AsyncOpenRouterClient:
    def __init__(
        self,
        api_key: str = OPENROUTER_API_KEY,
        base_url: str = OPENROUTER_BASE_URL,
        recorder=None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.recorder = recorder
        self.http = httpx.AsyncClient(
            timeout=httpx.Timeout(API_TIMEOUT_SECONDS, connect=30.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def close(self):
        await self.http.aclose()

    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stage: str = "",
    ) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        for attempt in range(MAX_RETRIES):
            try:
                resp = await self.http.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

                if self.recorder:
                    usage = data.get("usage", {})
                    self.recorder.record_api_call(
                        stage=stage,
                        model=model,
                        input_tokens=usage.get("prompt_tokens", 0),
                        output_tokens=usage.get("completion_tokens", 0),
                    )

                return data

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt < MAX_RETRIES - 1:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                else:
                    raise RuntimeError(
                        f"OpenRouter API failed after {MAX_RETRIES} attempts: {e}"
                    ) from e

    async def tool_calling_loop(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict],
        tool_executor,
        max_iterations: int = MAX_TOOL_ITERATIONS,
        stage: str = "",
        timeout: float = 600,
    ) -> tuple[list[dict], str]:
        try:
            return await asyncio.wait_for(
                self._tool_calling_loop_inner(
                    messages, model, tools, tool_executor, max_iterations, stage,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise RuntimeError(f"Tool calling loop timed out after {timeout}s")

    async def _tool_calling_loop_inner(
        self,
        messages: list[dict],
        model: str,
        tools: list[dict],
        tool_executor,
        max_iterations: int,
        stage: str,
    ) -> tuple[list[dict], str]:
        messages = list(messages)
        final_text = ""

        for _ in range(max_iterations):
            data = await self.chat_completion(
                messages=messages,
                model=model,
                tools=tools,
                stage=stage,
            )

            choices = data.get("choices")
            if not choices:
                raise RuntimeError(f"API response missing 'choices': {list(data.keys())}")

            choice = choices[0]
            assistant_msg = choice["message"]

            tool_calls = assistant_msg.get("tool_calls")
            if not tool_calls:
                final_text = assistant_msg.get("content", "")
                messages.append({"role": "assistant", "content": final_text})
                break

            messages.append(assistant_msg)

            for tc in tool_calls:
                func = tc["function"]
                tool_name = func["name"]
                try:
                    arguments = json.loads(func["arguments"])
                except json.JSONDecodeError:
                    arguments = {}

                start = time.time()
                result = await tool_executor.execute(tool_name, arguments)
                duration_ms = int((time.time() - start) * 1000)

                if self.recorder:
                    self.recorder.record_tool_call(
                        stage=stage,
                        tool_call=ToolCallRecord(
                            id=tc["id"],
                            name=tool_name,
                            arguments=arguments,
                            result=result,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            duration_ms=duration_ms,
                        ),
                    )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        return messages, final_text
