# MCP Client and Server Examples

This directory contains examples of Model Context Protocol (MCP) client and server implementations using the Python SDK.

## Files

- `mcp_client.py` - MCP client examples for stdio and HTTP transports
- `mcp_server.py` - Simple MCP server with tools, resources, and prompts
- `run_mcp_server.sh` - Wrapper script for Claude Desktop integration
- `README.md` - This file

## Installation

Install the MCP Python SDK:

```bash
pip install "mcp[cli]"
```

Or install from the requirements.txt in the parent directory:

```bash
pip install -r ../requirements.txt
```

## Running the Examples

### 1. Running the MCP Server

Start the server in stdio mode (default):

```bash
python mcp/mcp_server.py
# or explicitly
python mcp/mcp_server.py --transport stdio
```

Or start the server in HTTP mode:

```bash
python mcp/mcp_server.py --transport streamable-http --port 8000
```

You can also specify a different host and port:

```bash
python mcp/mcp_server.py --transport streamable-http --host 0.0.0.0 --port 9000
```

### 2. Running the MCP Client

The client will test both stdio and HTTP transports. For the best experience:

1. **First, run the client** (it will test stdio automatically):
   ```bash
   python mcp/mcp_client.py
   ```

2. **For HTTP testing**, when prompted:
   - Open a second terminal
   - Start the HTTP server: `python mcp/mcp_server.py --transport streamable-http --port 8000`
   - Return to the first terminal and press Enter to continue

### 3. Connecting to a Dockerized MCP Toolkit

If you have a Docker-based MCP toolkit that exposes many MCP servers on a single TCP port,
the client can connect through a `socat` bridge. The client automatically launches a Docker
container to pipe STDIO to the toolkit's TCP endpoint.

```bash
python mcp/mcp_client.py --host host.docker.internal --port 8811 --docker-image alpine/socat --list-tools
```

You can modify the host, port, or Docker image using the `--host`, `--port`, and
`--docker-image` options. Use `--tool <tool_name>` to call a specific tool after listing.

### 4. Testing with MCP Inspector

You can also test the server using the built-in MCP inspector:

```bash
mcp dev mcp/mcp_server.py
```

This will start an interactive inspector where you can test the server's capabilities.

**Note**: The MCP inspector works with stdio transport. For HTTP testing, use the client example above.

You can then connect MCP clients to `http://localhost:8000/mcp`

### 5. Claude Desktop Integration

To use this MCP server with Claude Desktop, you need to configure it to use the correct Python environment. There are two approaches:

#### Option 1: Using the Wrapper Script (Recommended)

Add this to your Claude Desktop configuration file (`~/Library/Application\ Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "/Users/<user>/LlamaBot/mcp/run_mcp_server.sh",
      "args": []
    }
  }
}
```

#### Option 2: Direct Python Path

Alternatively, use the virtual environment's Python directly:

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "/Users/<user>/LlamaBot/venv/bin/python",
      "args": ["/Users/<user>/LlamaBot/mcp/mcp_server.py"]
    }
  }
}
```

**Important Notes:**
- Replace the paths with your actual project directory
- The wrapper script (`run_mcp_server.sh`) automatically activates the virtual environment
- After updating the configuration, restart Claude Desktop
- Check the Claude Desktop logs for any connection issues

## Server Features

The example server (`mcp_server.py`) provides:

### Tools
- `echo(message: str)` - Echo a message back
- `add_numbers(a: int, b: int)` - Add two numbers
- `get_current_time()` - Get current timestamp
- `calculate_bmi(weight_kg: float, height_m: float)` - Calculate BMI

### Resources
- `config://server` - Server configuration
- `data://users/{user_id}` - User data by ID
- `system://status` - System status

### Prompts
- `review_code(code: str)` - Code review prompt
- `debug_error(error_message: str, context: str)` - Debugging prompt
- `explain_concept(concept: str)` - Concept explanation prompt

## Client Features

The example client (`mcp_client.py`) demonstrates:

### Stdio Transport
- Connecting to MCP servers via stdio
- Listing available resources, tools, and prompts
- Reading resources
- Calling tools
- Getting prompts

### HTTP Transport
- Connecting to MCP servers via HTTP
- Same operations as stdio transport
- Error handling for network issues

## Customization

You can modify the client to:
- Connect to different server URLs
- Add authentication (OAuth examples available in the SDK)
- Handle different tool schemas
- Implement custom sampling callbacks

You can modify the server to:
- Add more tools and resources
- Implement authentication
- Add database connections
- Support different transport modes

## Troubleshooting

1. **Server not found**: Make sure the server script path is correct in the client
2. **HTTP connection failed**: Ensure the HTTP server is running and the URL is correct
3. **Import errors**: Make sure the MCP SDK is installed with `pip install "mcp[cli]"`
4. **Permission errors**: Make sure the server script is executable

## Documentation

For more information, see:
- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://spec.modelcontextprotocol.io)