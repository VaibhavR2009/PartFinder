import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()
if 'GOOGLE_API_KEY' in os.environ and 'GEMINI_API_KEY' not in os.environ:
    os.environ['GEMINI_API_KEY'] = os.environ['GOOGLE_API_KEY']

from agents.orchestrator import run_pipeline
from api.models import ProjectRequest

req = {
  'description': 'Build a wooden planter box.',
  'budget_usd': 50,
  'zip_code': '90210',
  'skill_level': 'beginner',
  'tools_on_hand': ['drill']
}

async def run():
    async for event in run_pipeline(req):
        if event.get('stage') == 'complete':
            data = event.get('data', {})
            print('--- COMPLETED ---')
            print(json.dumps(data, indent=2))
        elif event.get('stage') in ['feasibility', 'sourcing', 'verification']:
            print(f"--- {event.get('stage').upper()} ---")
            print(json.dumps(event.get('data', {}), indent=2))

if __name__ == "__main__":
    asyncio.run(run())
