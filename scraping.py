import sqlite3
import requests
from bs4 import BeautifulSoup

# Define the maximum number of articles to store
MAX_ARTICLES = 5  # You can change this to 10 if you prefer

# Function to create a SQLite database and table if they don't exist
def create_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    link TEXT,
                    image TEXT
                )''')
    conn.commit()
    conn.close()

# Function to insert new articles into the database
def insert_news_to_db(news_items):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    
    # Insert new news items
    for title, link, image in news_items:
        c.execute('INSERT INTO news (title, link, image) VALUES (?, ?, ?)', (title, link, image))
    
    # Delete the oldest articles if the count exceeds MAX_ARTICLES
    c.execute('DELETE FROM news WHERE id NOT IN (SELECT id FROM news ORDER BY id DESC LIMIT ?)', (MAX_ARTICLES,))
    
    conn.commit()
    conn.close()

# Function to fetch the latest news from the URL
def fetch_latest_news():
    url = "https://wiadomosci.wp.pl/polska"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all news blocks using the updated class name
    news_blocks = soup.find_all('div', class_='f2eMLotm')
    all_news = []
    
    print(f"Found {len(news_blocks)} news blocks.")  # Debug print
    
    for block in news_blocks[:MAX_ARTICLES]:  # Only take the top MAX_ARTICLES news items
        # Extract headline
        headline_tag = block.find('h2', class_='teaserTitle--isBig')
        if not headline_tag:
            headline_tag = block.find('h3', class_='teaserTitle--isBig')  # Check for <h3> if <h2> is not found
        if not headline_tag:
            headline_tag = block.find('h2')  # Fallback: Look for any <h2> tag
        if not headline_tag:
            headline_tag = block.find('h3')  # Fallback: Look for any <h3> tag
        
        headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"
        
        # Extract link
        link_tag = block.find('a', class_='f2PrHTUx', href=True)
        link = link_tag['href'] if link_tag else "No URL found"
        if link.startswith('/'):
            link = 'https://wiadomosci.wp.pl' + link
        
        # Extract image URL
        img_tag = block.find('img', class_='f3BQvntU')
        img_url = img_tag['src'] if img_tag else "No image found"
        
        # Debug print to check extracted data
        print(f"Headline: {headline}, Link: {link}, Image: {img_url}")
        
        # Append the extracted data to the list
        all_news.append([headline, link, img_url])
    
    return all_news

# Main function to check if any new news should be inserted
def update_news_in_db():
    create_db()
    
    # Fetch the latest news
    latest_news = fetch_latest_news()
    
    # Filter out articles with invalid headlines
    valid_news = [news for news in latest_news if news[0] != "No headline found"]
    
    # Get the existing news from the database
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute('SELECT title FROM news')
    existing_titles = {row[0] for row in c.fetchall()}
    conn.close()
    
    print(f"Existing titles in DB: {existing_titles}")  # Debug print
    
    # Filter out the news that already exists in the database
    new_news = [news for news in valid_news if news[0] not in existing_titles]
    
    # Insert the new news into the database
    if new_news:
        insert_news_to_db(new_news)
        print(f"Inserted {len(new_news)} new articles into the database.")
    else:
        print("No new articles to insert.")

# Run the update process
update_news_in_db()