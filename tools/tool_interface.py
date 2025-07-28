# tools/tool_interface.py

from abc import ABC, abstractmethod

class ToolInterface(ABC):
    """
    Abstract base class for all MCP-compatible tools.
    Each tool must implement the `run()` method.
    """

    name: str = "unnamed_tool"
    description: str = "No description provided."

    @abstractmethod
    def run(self, input_data):
        """
        Executes the tool logic.

        Args:
            input_data (any): Input passed to the tool, typically a dict or string.

        Returns:
            any: The result of the tool’s operation (e.g., str, dict, or None).
        """
        pass


