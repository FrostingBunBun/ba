import requests
from bs4 import BeautifulSoup
import os

# Constants
URL = "https://wiadomosci.wp.pl/polska"
MAX_ARTICLES = 5  # Fetch all articles from the page
MAX_PROCESSED_LINKS = 9  # Maximum number of links to store in the file
PROCESSED_FILE = "processed_articles.txt"  # File to store processed article links

def loadProcessedArticles():
    """Load the list of processed article links from the file."""
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as file:
            processed_articles = file.read().splitlines()  # Return a list of links
            return processed_articles
    except FileNotFoundError:
        return []

def saveProcessedArticles(processed_articles):
    """Save the list of processed article links to the file, keeping only the most recent MAX_PROCESSED_LINKS."""
    # Keep only the most recent MAX_PROCESSED_LINKS links
    if len(processed_articles) > MAX_PROCESSED_LINKS:
        processed_articles = processed_articles[-MAX_PROCESSED_LINKS:]
    
    with open(PROCESSED_FILE, "w", encoding="utf-8") as file:
        for entry in processed_articles:
            file.write(entry + "\n")

def fetchLatestNews():
    """Fetch the latest news articles from the website."""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        newsBlocks = soup.find_all('div', class_='f2eMLotm')[:MAX_ARTICLES]  # Fetch all articles
        latestNews = []

        for block in newsBlocks:
            headlineTag = block.find('h2', class_='teaserTitle--isBig') or block.find('h3', class_='teaserTitle--isBig') or block.find('h2') or block.find('h3')
            headline = headlineTag.get_text(strip=True) if headlineTag else "No headline found"

            linkTag = block.find('a', class_='f2PrHTUx', href=True)
            link = linkTag['href'] if linkTag else "No URL found"
            if link.startswith('/'):
                link = 'https://wiadomosci.wp.pl' + link

            # Find the image link
            imageTag = block.find('img', src=True)
            imageLink = imageTag['src'] if imageTag else "No image URL found"

            if headline != "No headline found" and link != "No URL found":
                latestNews.append({"title": headline, "link": link, "image_link": imageLink})

        return latestNews
    except requests.RequestException as e:
        print(f"Failed to fetch news: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error while fetching news: {e}")
        return []

def getNewArticles():
    """Compare the latest articles with the processed list and return new articles."""
    # Load processed articles
    processed_articles = loadProcessedArticles()

    # Fetch the latest articles
    latest_articles = fetchLatestNews()
    if not latest_articles:
        return []

    # Find new articles
    new_articles = []
    for article in latest_articles:
        # Extract only the article link from the processed articles (before the '|')
        article_link = article["link"]
        
        # Check if this article's link is in the processed articles (only the article part, not image)
        if not any(article_link == entry.split(' | ')[0] for entry in processed_articles):
            new_articles.append(article)

    # Update the processed articles list
    for article in new_articles:
        # Save the article link and image link separated by a special symbol (e.g., '|')
        entry = f"{article['link']} | {article['image_link']}"
        processed_articles.append(entry)  # Add new entry to the end of the list

    # Save the updated list of processed articles
    saveProcessedArticles(processed_articles)

    return new_articles
