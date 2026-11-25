"""Standalone stdio entry point: python -m mcp_server.server."""

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from .syllable_counter import syllable_counter
from .rhyme_checker import rhyme_checker
from .retrieve_context import retrieve_context


server = MCPServer("Transylvanian Folk & Rap")
for tool in (syllable_counter, rhyme_checker, retrieve_context):
    server.tool(
        annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
        structured_output=True,
    )(tool)


if __name__ == "__main__":
    server.run(transport="stdio")
