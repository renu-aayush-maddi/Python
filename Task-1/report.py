import csv

def generate_report(changes):
    if not changes:
        print("No price changes")
        return
    
    print("\nPrice Changes:\n")
    for c in changes:
        print(c["name"])
        print(f"£{c['old_price']} -> £{c['new_price']} ({c['change']}%)")
        print("-"*30)

    print(f"Total:{len(changes)}")

    with open("price_changes.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name","Old Price","New Price","Change (%)"])
        for c in changes:
            writer.writerow([c["name"],c["old_price"],c["new_price"],c["change"]])