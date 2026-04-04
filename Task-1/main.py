import asyncio
import random
from playwright.async_api import async_playwright
from config import TOTAL_PAGES,USER_AGENTS
from db import setup_db
from scraper import scrape_page
from processor import update_check
from report import generate_report

async def main():
    conn = await setup_db()
    all_products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for i in range(1,TOTAL_PAGES+1):
            ua = random.choice(USER_AGENTS)
            context = await browser.new_context(user_agent=ua)
            page = await context.new_page()
            data = await scrape_page(page,i)
            all_products.extend(data)
            
    changes = await update_check(conn,all_products)
    generate_report(changes)
    
if __name__ == "__main__":
    asyncio.run(main())