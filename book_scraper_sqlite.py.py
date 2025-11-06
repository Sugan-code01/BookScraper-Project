import requests
from bs4 import BeautifulSoup
import sqlite3
from time import sleep
import os

# -------------------- DATABASE CONFIG -------------------- #
DB_FILE = "books.db"  # SQLite database file

# -------------------- CONNECT TO SQLITE -------------------- #
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
print(f"✅ Connected to SQLite database: {DB_FILE}")

# -------------------- CREATE TABLE -------------------- #
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price TEXT,
    rating TEXT,
    link TEXT
)
""")
conn.commit()
print("✅ Table 'books' is ready")

# -------------------- CLEAR TABLE -------------------- #
cursor.execute("DELETE FROM books")
conn.commit()
print("🗑️ Cleared existing rows from books")

# -------------------- HELPER FUNCTION -------------------- #
def rating_text_from_class(tag):
    """Convert star-rating class to readable text"""
    classes = tag.get("class", [])
    for c in classes:
        if c.lower() in ("one", "two", "three", "four", "five"):
            return c.capitalize()
    return "N/A"

# -------------------- SCRAPER FUNCTION -------------------- #
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

def scrape_books(limit=50):
    books_scraped = 0
    page = 1
    print("\n🚀 Starting BookScraper with SQLite3...\n")

    while books_scraped < limit:
        url = BASE_URL.format(page)
        print(f"🔎 Fetching page {page}: {url}")
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(".product_pod")

        if not items:
            print("⚠️ No books found. Stopping.")
            break

        for book in items:
            title = book.h3.a["title"]
            price = book.select_one(".price_color").text.strip()
            rating = rating_text_from_class(book.p)
            link = "https://books.toscrape.com/catalogue/" + book.h3.a["href"]

            cursor.execute("""
                INSERT INTO books (title, price, rating, link)
                VALUES (?, ?, ?, ?)
            """, (title, price, rating, link))
            conn.commit()

            books_scraped += 1
            print(f"{books_scraped}. {title} | {price} | {rating}")

            if books_scraped >= limit:
                break

        page += 1
        sleep(1)

    print(f"\n✅ Scraped {books_scraped} books and stored in SQLite successfully!")

# -------------------- RUN SCRIPT -------------------- #
if __name__ == "__main__":
    scrape_books()
    cursor.close()
    conn.close()
