#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('backend')
from app.services.llm import LLMService

async def test_simple():
    print("Testing legacy extraction...")
    llm = LLMService()
    result = await llm.analyze_cover_sheet('tests/standard.pdf')
    print('Legacy extraction working:', bool(result.title))
    print('Title:', result.title)
    print('Entity Status:', result.entity_status)
    print('Total Drawing Sheets:', result.total_drawing_sheets)
    print('Inventors:', len(result.inventors))
    for i, inv in enumerate(result.inventors):
        print(f'  {i+1}. {inv.first_name} {inv.middle_name or ""} {inv.last_name}')
        print(f'     Citizenship: {inv.citizenship}')
        print(f'     Address: {inv.street_address}, {inv.city}, {inv.state}')

if __name__ == "__main__":
    asyncio.run(test_simple())