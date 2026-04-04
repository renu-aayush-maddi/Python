from datetime import datetime

async def update_check(conn, data):
    changes = []
    now = datetime.now()

    for item in data:
        row = await conn.fetchrow("SELECT price FROM products WHERE sku=$1",item["sku"])
        if row:
            old_price = row["price"]
            if round(old_price, 2) != round(item["price"],2):
                change = ((item["price"] - old_price) / old_price) * 100
                changes.append({
                    "name": item["name"],
                    "old_price": old_price,
                    "new_price": item["price"],
                    "change": round(change,1)
                })

                await conn.execute("""
                    UPDATE products
                    SET price=$1,last_updated=$2
                    WHERE sku=$3
                """,item["price"],now,item["sku"])

        else:
            await conn.execute("""
                INSERT INTO products (sku,name,price,last_updated)
                VALUES ($1,$2,$3,$4)
            """,item["sku"],item["name"],item["price"],now)
    return changes