from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv
load_dotenv()

llama_docs = SimpleDirectoryReader("./llamaindex_docs").load_data()
llama_index = VectorStoreIndex.from_documents(llama_docs)
llama_query_engine = llama_index.as_query_engine()

github_docs = SimpleDirectoryReader("./github_docs").load_data()
github_index = VectorStoreIndex.from_documents(github_docs)
github_query_engine = github_index.as_query_engine()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SearchServer")

@mcp.tool()
def search_llama_docs(query: str) -> str:
    """llamaindex 문서에서 질의에 맞는 내용을 검색합니다."""
    return llama_query_engine.query(query).response

@mcp.tool()
def search_github_docs(query: str) -> str:
    """깃허브 문서에서 질의에 맞는 내용을 검색합니다."""
    return github_query_engine.query(query).response

if __name__ == "__main__":
    mcp.run(transport="sse")
