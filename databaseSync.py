import sqlite3
import requests
from bs4 import BeautifulSoup

DB_FILE = "news.db"
MAX_ARTICLES = 5
TEST_MODE = False  # Set to False to fetch real data from the website

def createDb():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS news (title TEXT UNIQUE, link TEXT)")
    except sqlite3.Error as e:
        print(f"DB Error: {e}")

def fetchLatestNews():
    if TEST_MODE:
        return [
            {"title": "Breaking: Test 1", "link": "https://example.com/test1"},
            {"title": "Breaking News: Test 2", "link": "https://example.com/test2"},
            {"title": "Exclusive: Test 3", "link": "https://example.com/test3"},
            {"title": "Latest Update: Test 4", "link": "https://example.com/test4"},
            {"title": "Special Report: Test 5", "link": "https://example.com/test5"},
        ]
    else:
        url = "https://wiadomosci.wp.pl/polska"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_blocks = soup.find_all('div', class_='f2eMLotm')
        latest_news = []
        
        for block in news_blocks[:MAX_ARTICLES]:
            headline_tag = block.find('h2', class_='teaserTitle--isBig') or block.find('h3', class_='teaserTitle--isBig') or block.find('h2') or block.find('h3')
            headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"
            
            link_tag = block.find('a', class_='f2PrHTUx', href=True)
            link = link_tag['href'] if link_tag else "No URL found"
            if link.startswith('/'):
                link = 'https://wiadomosci.wp.pl' + link
            
            if headline != "No headline found" and link != "No URL found":
                latest_news.append({"title": headline, "link": link})
        
        return latest_news

def getDbArticles():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return [{"title": row[0], "link": row[1]} for row in conn.execute(
                "SELECT title, link FROM news ORDER BY ROWID DESC LIMIT ?", (MAX_ARTICLES,)
            )]
    except sqlite3.Error as e:
        print(f"DB Fetch Error: {e}")
        return []

def updateNewsToDb(newArticles):
    if not newArticles:
        return

    try:
        with sqlite3.connect(DB_FILE) as conn:
            # Insert new articles at the top
            for article in reversed(newArticles):  # Reverse to maintain order (newest first)
                conn.execute("INSERT OR IGNORE INTO news (title, link) VALUES (?, ?)", (article["title"], article["link"]))
            
            # Delete older articles beyond MAX_ARTICLES
            conn.execute(f"DELETE FROM news WHERE ROWID NOT IN (SELECT ROWID FROM news ORDER BY ROWID DESC LIMIT {MAX_ARTICLES})")
            conn.commit()
    except sqlite3.Error as e:
        print(f"DB Update Error: {e}")

def syncNews():
    createDb()
    latestNews = fetchLatestNews()
    if not latestNews:
        return []

    dbArticles = getDbArticles()
    newArticles = [article for article in latestNews if article not in dbArticles]

    if newArticles:
        updateNewsToDb(newArticles)

    return newArticles

newArticles = syncNews()
print("New Articles:", newArticles)
print("LEN:", len(newArticles))