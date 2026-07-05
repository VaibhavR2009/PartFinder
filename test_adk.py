import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai.types import Content, Part
from agents.config import GEMINI_MODEL

async def test():
    mcp_toolset = McpToolset(connection_params=StreamableHTTPConnectionParams(url="http://localhost:8001/mcp"))
    agent = LlmAgent(
        model=GEMINI_MODEL,
        name="test_agent",
        tools=[mcp_toolset],
        instruction="Use Home Depot search to find an arduino.",
    )
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test", user_id="u1")
    runner = Runner(agent=agent, app_name="test", session_service=session_service)

    print("Running...")
    async for event in runner.run_async(
        user_id="u1",
        session_id=session.id,
        new_message=Content(role="user", parts=[Part(text="Find me an arduino at Home Depot and output JSON.")]),
    ):
        print(f"EVENT TYPE: {type(event)}")
        if hasattr(event, 'content') and event.content:
            print(f"  CONTENT: {event.content}")
            for p in event.content.parts:
                print(f"    PART: {type(p)}")
                if hasattr(p, 'text'):
                    print(f"    TEXT: {p.text!r}")
        if hasattr(event, 'is_final_response'):
            print(f"  IS_FINAL: {event.is_final_response()}")

    await mcp_toolset.close()

if __name__ == "__main__":
    asyncio.run(test())
