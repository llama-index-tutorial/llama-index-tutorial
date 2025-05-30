import json
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# MCP 서버 연결
mcp_client = BasicMCPClient("http://localhost:8000/sse")
mcp_tool_spec = McpToolSpec(client=mcp_client)

tools = mcp_tool_spec.to_tool_list()
for tool in tools:
    tool_dict = {
        "name": tool.metadata.name,
        "description": tool.metadata.description,
        "parameters": json.loads(tool.metadata.fn_schema_str)
    }
    print(json.dumps(tool_dict, indent=2, ensure_ascii=False))
