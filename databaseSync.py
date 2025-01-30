import sqlite3

DB_FILE = "news.db"
MAX_ARTICLES = 5
TEST_MODE = False

TEST_ARTICLES = [
    {"title": "Breaking: Test 1", "link": "https://example.com/test1"},
    {"title": "Breaking News: Test 2", "link": "https://example.com/test2"},
    {"title": "Exclusive: Test 3", "link": "https://example.com/test3"},
    {"title": "Latest Update: Test 4", "link": "https://example.com/test4"},
    {"title": "Special Report: Test 5", "link": "https://example.com/test5"},
]


def createDb():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS news (title TEXT UNIQUE, link TEXT)")
    except sqlite3.Error as e:
        print(f"DB Error: {e}")


def fetchLatestNews():
    return TEST_ARTICLES if TEST_MODE else []  # Replace with real data fetching


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
            conn.executemany("INSERT OR IGNORE INTO news (title, link) VALUES (?, ?)", 
                             [(article["title"], article["link"]) for article in newArticles])
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