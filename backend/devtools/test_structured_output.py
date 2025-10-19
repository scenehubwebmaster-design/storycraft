"""
Moved manual structured output test script.
Run manually from backend package root:

    python -m backend.devtools.test_structured_output

This is a manual dev script and not intended for pytest collection.
"""
import asyncio
from backend.test_structured_output import main as _main

if __name__ == "__main__":
    asyncio.run(_main())
"""
Manual structured output test script (moved from repository root). Run manually, not via pytest.
"""
import asyncio
import os
import json

from backend.schemas import CharacterGenerationRequest, WorldGenerationRequest
from backend.routers.generation import generate_character_structured, generate_world_structured


async def main():
    print("This is a manual test runner for structured output. Run this script only when you have API keys configured.")

if __name__ == '__main__':
    asyncio.run(main())
