import sqlite3
import requests
from bs4 import BeautifulSoup

# Constants
DB_FILE = "news.db"
MAX_ARTICLES = 5
URL = "https://wiadomosci.wp.pl/polska"

# Create the database and table if they don't exist
def createDb():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    title TEXT UNIQUE,
                    link TEXT UNIQUE
                )
            """)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise

# Fetch the latest news from the website
def fetchLatestNews():
    try:
        response = requests.get(URL, timeout=10)  # Add timeout for robustness
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        newsBlocks = soup.find_all('div', class_='f2eMLotm')[:MAX_ARTICLES]
        latestNews = []

        for block in newsBlocks:
            headlineTag = block.find('h2', class_='teaserTitle--isBig') or block.find('h3', class_='teaserTitle--isBig') or block.find('h2') or block.find('h3')
            headline = headlineTag.get_text(strip=True) if headlineTag else "No headline found"

            linkTag = block.find('a', class_='f2PrHTUx', href=True)
            link = linkTag['href'] if linkTag else "No URL found"
            if link.startswith('/'):
                link = 'https://wiadomosci.wp.pl' + link

            if headline != "No headline found" and link != "No URL found":
                latestNews.append({"title": headline, "link": link})

        return latestNews
    except requests.RequestException as e:
        print(f"Failed to fetch news: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error while fetching news: {e}")
        return []

# Get the current articles from the database
def getDbArticles():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute("SELECT title, link FROM news")
            return [{"title": row[0], "link": row[1]} for row in cursor]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

# Update the database with new articles
def updateDb(newArticles):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Insert new articles
            for article in newArticles:
                conn.execute("INSERT OR IGNORE INTO news (title, link) VALUES (?, ?)", (article["title"], article["link"]))

            # Delete older articles beyond MAX_ARTICLES
            conn.execute(f"DELETE FROM news WHERE rowid NOT IN (SELECT rowid FROM news ORDER BY rowid DESC LIMIT {MAX_ARTICLES})")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise

def syncNews():
    try:
        createDb()
        latestNews = fetchLatestNews()
        if not latestNews:
            return []

        dbArticles = getDbArticles()
        dbLinks = {article["link"] for article in dbArticles}  # Use a set of links for comparison
        newArticles = [article for article in latestNews if article["link"] not in dbLinks]

        if newArticles:
            updateDb(newArticles)

        return newArticles
    except Exception as e:
        print(f"Unexpected error in syncNews: {e}")
        return []


# if __name__ == "__main__":
#     newArticles = syncNews()

#     print('newArtiucles: ', newArticles)
#     print("LEN: ", len(newArticles))
