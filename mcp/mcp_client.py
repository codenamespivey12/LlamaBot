import asyncio
import json
import os
import argparse
from typing import Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


# Default configuration values for the Docker-based MCP bridge
DEFAULT_DOCKER_IMAGE = os.getenv("MCP_DOCKER_IMAGE", "alpine/socat")
DEFAULT_MCP_HOST = os.getenv("MCP_HOST", "host.docker.internal")
DEFAULT_MCP_PORT = int(os.getenv("MCP_PORT", "8811"))


async def handle_sampling_message(
    message: types.CreateMessageRequestParams,
) -> types.CreateMessageResult:
    """Optional sampling callback for handling model requests."""
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello from MCP client!",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )


async def demo_stdio_client(
    host: str = DEFAULT_MCP_HOST,
    port: int = DEFAULT_MCP_PORT,
    docker_image: str = DEFAULT_DOCKER_IMAGE,
    tool_name: Optional[str] = None,
    list_only: bool = False,
):
    """Connect to the MCP toolkit using a Docker-based stdio bridge."""
    print("=== MCP Stdio Client Demo ===")

    # Build docker command for socat bridge
    docker_args = [
        "run",
        "-i",
        "--rm",
        docker_image,
        "STDIO",
        f"TCP:{host}:{port}",
    ]

    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="docker",
        args=docker_args,
        env=None,
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read, write, sampling_callback=handle_sampling_message
            ) as session:
                # Initialize the connection
                print("Initializing connection...")
                await session.initialize()
                print("✓ Connection initialized")

                # List available prompts
                print("\n--- Listing Prompts ---")
                try:
                    prompts = await session.list_prompts()
                    if prompts.prompts:
                        for prompt in prompts.prompts:
                            print(f"Prompt: {prompt.name} - {prompt.description}")
                    else:
                        print("No prompts available")
                except Exception as e:
                    print(f"Error listing prompts: {e}")

                # List available resources
                print("\n--- Listing Resources ---")
                try:
                    resources = await session.list_resources()
                    if resources.resources:
                        for resource in resources.resources:
                            print(f"Resource: {resource.uri} - {resource.name}")
                    else:
                        print("No resources available")
                except Exception as e:
                    print(f"Error listing resources: {e}")

                # List available tools
                print("\n--- Listing Tools ---")
                tools = None
                try:
                    tools = await session.list_tools()
                    if tools.tools:
                        for tool in tools.tools:
                            print(f"Tool: {tool.name} - {tool.description}")
                    else:
                        print("No tools available")
                except Exception as e:
                    print(f"Error listing tools: {e}")

                if list_only:
                    return

                # Determine which tool to call
                selected_tool_name = tool_name
                if not selected_tool_name and tools and tools.tools:
                    selected_tool_name = tools.tools[0].name

                # Call the selected tool
                if selected_tool_name:
                    print(f"\n--- Calling Tool: {selected_tool_name} ---")

                    tool_args = {}
                    if tools and tools.tools:
                        selected = next((t for t in tools.tools if t.name == selected_tool_name), None)
                        if selected and getattr(selected, "inputSchema", None):
                            schema = selected.inputSchema
                            if "properties" in schema:
                                for prop_name, prop_def in schema["properties"].items():
                                    if prop_def.get("type") == "string":
                                        tool_args[prop_name] = "example"
                                    elif prop_def.get("type") == "integer":
                                        tool_args[prop_name] = 42
                                    elif prop_def.get("type") == "number":
                                        tool_args[prop_name] = 3.14

                    try:
                        result = await session.call_tool(selected_tool_name, arguments=tool_args)
                        print(f"Tool result: {result.content}")
                    except Exception as e:
                        print(f"Error calling tool '{selected_tool_name}': {e}")

    except Exception as e:
        print(f"Stdio client error: {e}")


async def demo_http_client(server_url: str = "http://localhost:8000/mcp"):
    """Demonstrate MCP client using HTTP transport."""
    print("\n=== MCP HTTP Client Demo ===")
    print(f"Attempting to connect to: {server_url}")
    
    try:
        # Connect to a streamable HTTP server
        async with streamablehttp_client(server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            # Create a session using the client streams
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                print("Initializing HTTP connection...")
                await session.initialize()
                print("✓ HTTP Connection initialized")

                # List available tools
                print("\n--- Listing Tools (HTTP) ---")
                try:
                    tools = await session.list_tools()
                    if tools.tools:
                        for tool in tools.tools:
                            print(f"Tool: {tool.name} - {tool.description}")
                            
                        # Try calling the first tool with example data
                        if tools.tools:
                            tool_name = tools.tools[0].name
                            print(f"\n--- Calling Tool via HTTP: {tool_name} ---")
                            
                            # Example: if it's an echo tool
                            if "echo" in tool_name.lower():
                                result = await session.call_tool(tool_name, arguments={"message": "Hello via HTTP!"})
                                print(f"Tool result: {result.content}")
                            else:
                                # Try with generic arguments
                                result = await session.call_tool(tool_name, arguments={})
                                print(f"Tool result: {result.content}")
                    else:
                        print("No tools available")
                except Exception as e:
                    print(f"Error with HTTP operations: {e}")

                # List resources
                print("\n--- Listing Resources (HTTP) ---")
                try:
                    resources = await session.list_resources()
                    if resources.resources:
                        for resource in resources.resources:
                            print(f"Resource: {resource.uri} - {resource.name}")
                    else:
                        print("No resources available")
                except Exception as e:
                    print(f"Error listing resources via HTTP: {e}")

    except ConnectionError as e:
        print(f"HTTP connection failed: {e}")
        print(f"Make sure an MCP server is running at {server_url}")
        print("To start the server in HTTP mode, run:")
        print("  python mcp/mcp_server.py --transport streamable-http --port 8000")
    except Exception as e:
        print(f"HTTP client error: {e}")
        print(f"This might be because no server is running at {server_url}")
        print("To start the server in HTTP mode, run:")
        print("  python mcp/mcp_server.py --transport streamable-http --port 8000")


async def main():
    """Entry point for connecting to the MCP toolkit."""
    parser = argparse.ArgumentParser(description="Connect to a Docker-hosted MCP toolkit")
    parser.add_argument("--host", default=DEFAULT_MCP_HOST, help="Toolkit host")
    parser.add_argument("--port", type=int, default=DEFAULT_MCP_PORT, help="Toolkit port")
    parser.add_argument("--docker-image", default=DEFAULT_DOCKER_IMAGE, help="Docker image for socat bridge")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    parser.add_argument("--tool", help="Call a specific tool by name")
    parser.add_argument("--http-url", help="Optional HTTP server URL for testing")

    args = parser.parse_args()

    if args.http_url:
        await demo_http_client(server_url=args.http_url)
        return

    await demo_stdio_client(
        host=args.host,
        port=args.port,
        docker_image=args.docker_image,
        tool_name=args.tool,
        list_only=args.list_tools,
    )


if __name__ == "__main__":
    asyncio.run(main())