"""Standalone stdio entry point: python -m mcp_server.server."""

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from .syllable_counter import syllable_counter


server = MCPServer("Transylvanian Folk & Rap")
server.tool(annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))(
    syllable_counter
)


if __name__ == "__main__":
    server.run(transport="stdio")
