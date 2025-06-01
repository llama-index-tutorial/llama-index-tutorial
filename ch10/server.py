from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def summarize_text(text: str) -> str:
    """긴 텍스트를 요약해 간결하게 반환합니다."""
    return text[:100] + "..."

if __name__ == "__main__":
    mcp.run(transport="sse")