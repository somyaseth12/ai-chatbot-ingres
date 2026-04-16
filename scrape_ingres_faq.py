import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://ingres.iith.ac.in"

headers = {
    "User-Agent": "Mozilla/5.0"
}

groundwater_data = []

def scrape_page(url):
    print(f"Scraping: {url}")
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")

    if not table:
        print("No table found")
        return []

    rows = table.find_all("tr")[1:]  # skip header

    data = []

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        try:
            record = {
                "state": cols[0].text.strip(),
                "district": cols[1].text.strip(),
                "year": int(cols[2].text.strip()),
                "category": cols[3].text.strip(),
                "extraction": float(cols[4].text.strip().replace('%','')),
                "recharge": float(cols[5].text.strip()) if len(cols) > 5 else 0
            }

            data.append(record)

        except Exception as e:
            continue

    return data


def scrape_multiple_years():
    years = [2020, 2021, 2022, 2023]   # 👈 extend later

    all_data = []

    for year in years:
        url = f"{BASE_URL}/some-data-page?year={year}"  # ⚠ replace with actual endpoint
        
        page_data = scrape_page(url)
        all_data.extend(page_data)

        time.sleep(2)  # avoid blocking

    return all_data


def remove_duplicates(data):
    unique = []
    seen = set()

    for item in data:
        key = (item["district"], item["year"])

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


def save_data(data):
    with open("groundwater_data.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    print("🚀 Starting scraper...")

    data = scrape_multiple_years()

    data = remove_duplicates(data)

    print(f"✅ Total records: {len(data)}")

    save_data(data)

    print("📁 Data saved to groundwater_data.json")