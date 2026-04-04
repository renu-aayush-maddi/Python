from config import TOTAL_PAGES

async def scrape_page(page, page_num):
    url = f"http://books.toscrape.com/catalogue/page-{page_num}.html"
    await page.goto(url)
    products = []
    books = await page.locator("article.product_pod").all()

    for book in books:
        title = book.locator("h3 a")
        price_el = book.locator(".price_color")

        sku = await title.get_attribute("href")
        name = await title.get_attribute("title")
        price = float((await price_el.inner_text()).replace("£",""))

        products.append({
            "sku": sku,
            "name": name,
            "price": price
        })

    print(f"Page {page_num}/{TOTAL_PAGES} done")
    return products