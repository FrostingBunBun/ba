import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def fetchPage(link, timeout=10):
    try:
        response = requests.get(link, timeout=timeout)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Page fetch error: {e}")
        return None

def cleanText(text):
    text = re.sub(r'\\[nrt]|\\"|\s+', ' ', str(text))
    text = re.sub(r'\\u[0-9A-Fa-f]{4}', '', text)
    return text.strip()

def extractContent(link):
    try:
        htmlContent = fetchPage(link)
        if not htmlContent:
            return {"error": "Failed to fetch page"}

        soup = BeautifulSoup(htmlContent, 'html.parser')
        
        # Try to find the <h1> tag - more flexible search
        titleTag = soup.find('h1')
        
        # If no <h1> tag found, log a warning
        if not titleTag:
            logging.warning("No <h1> tag found, looking for title in other tags...")
            titleTag = soup.find('title')  # Try the <title> tag as a fallback
        
        article = soup.find('article', id='main-content')

        if not article:
            return {"error": "Main content not found"}

        read_more_patterns = [
            'Czytaj też:', 
            'Czytaj więcej:', 
            'Więcej informacji:', 
            'Zobacz również:', 
            'Polecane artykuły:', 
            'Powiązane treści:',
            'Dodatkowe informacje:',
            'Źródło:'
        ]

        paragraphs = []
        for p in article.find_all('p'):
            text = cleanText(p.get_text())
            
            if any(pattern in text for pattern in read_more_patterns):
                break
            
            if len(text.split()) > 5:
                paragraphs.append(text)

        content = " ".join(paragraphs)
        content = re.sub(r'http[s]?://\S+|<.*?>', '', content)

        return {
            "title": cleanText(titleTag.get_text()) if titleTag else "No title",
            "content": content,
            "images": [img['src'] for img in article.find_all('img', src=True)],
            "publicationTime": soup.find('time')['datetime'] if soup.find('time') else "No time"
        }
    except Exception as e:
        logging.error(f"Content extraction error: {e}")
        return {"error": str(e)}

def getPageData(link):
    result = extractContent(link)
    
    if "error" in result:
        logging.error(result["error"])
        return None
    
    return f"'Title: {result['title']}, Content: {result['content']}'"

# result = getPageData('https://wiadomosci.wp.pl/czolowe-zderzenie-i-dachowanie-za-kierownica-20-latek-7120719323319104a')
# print(result)
