from .definitions import TOOL_DEFINITIONS


class ToolRegistry:
    def __init__(self):
        self.tools = {t["function"]["name"]: t for t in TOOL_DEFINITIONS}

    def get_openai_tools(self) -> list[dict]:
        return list(self.tools.values())

    def get_tool_names(self) -> list[str]:
        return list(self.tools.keys())
