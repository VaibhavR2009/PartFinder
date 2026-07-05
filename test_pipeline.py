import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()
from agents.orchestrator import run_pipeline

logging.basicConfig(level=logging.INFO)

async def test():
    project_input = {
        "budget_usd": 300,
        "zip_code": "08889",
        "description": "A robotic monitor arm that can be used (we have a 3d printer) and moves based on the location of the user. We have an arduino and a monitor to use. we are using google mediapipe to detect the user.",
        "skill_level": "intermediate",
        "tools_on_hand": []
    }
    async for event in run_pipeline(project_input):
        print(f"PIPELINE EVENT: {event}")

if __name__ == "__main__":
    asyncio.run(test())
