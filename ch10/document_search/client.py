from llama_index.tools.mcp import BasicMCPClient
from dotenv import load_dotenv
load_dotenv()

# MCP 서버 연결
mcp_client = BasicMCPClient("http://localhost:8000/sse")

from llama_index.tools.mcp import McpToolSpec

# MCP 도구를 LlamaIndex용으로 변환
tool_spec = McpToolSpec(client=mcp_client)

# FunctionTool 리스트 획득
tools = tool_spec.to_tool_list()


from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent

# LLM 설정 (gpt-4o-mini 사용)
llm = OpenAI(model="gpt-4o-mini")

# FunctionAgent 생성
agent = FunctionAgent(
    tools=tools,
    llm=llm,
    system_prompt=(
        "사용자의 질문을 분석하여, LlamaIndex 문서나 GitHub 문서 중 적절한 문서를 검색하는 도구를 선택하고, "
        "그 결과를 바탕으로 구체적인 예시와 함께 답변을 생성하는 에이전트입니다."
    ),
)

import asyncio

async def run_agent():
    question = "Llama-Index를 활용하여 문서 검색하는 방법"
    response = await agent.run(question)
    print("\n=== 에이전트 응답 ===\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(run_agent())
