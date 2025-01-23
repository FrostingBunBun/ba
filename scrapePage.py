import requests
from bs4 import BeautifulSoup
import json

def fetch_and_clean_article(link):
    response = requests.get(link)
    if response.status_code != 200:
        return {"error": f"Failed to fetch page, status code: {response.status_code}"}
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.find('title').get_text(strip=True) if soup.find('title') else "No title found"

    article = soup.find('article', id='main-content')
    if not article:
        return {"error": "No article with id 'main-content' found"}

    raw_paragraphs = article.find_all('p')
    paragraphs = []
    
    for p in raw_paragraphs:
        text = p.get_text(strip=True)
        if len(text.split()) > 5:  # filter out short
            paragraphs.append(text)
    
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        if paragraph not in cleaned_paragraphs:
            cleaned_paragraphs.append(paragraph)
    
    content = " ".join(cleaned_paragraphs)

    images = [img['src'] for img in article.find_all('img', src=True)]
    
    publication_time = soup.find('time')['datetime'] if soup.find('time') else "No publication time found"

    return {
        "title": title,
        "content": content,
        "images": images,
        "publication_time": publication_time
    }


link = "https://wiadomosci.wp.pl/bawaria-atak-nozownika-wsrod-ofiar-dziecko-7117015738010400a"
article_data = fetch_and_clean_article(link)

print(json.dumps(article_data, indent=4, ensure_ascii=False))

# fix Bild" informuje, że nie ma obecnie zagrożenia dla ludności.

# Przeczytaj także: !!!!


# Sprawa syna posłanki PiS w sądzie. Od postawienia zarzutów minęło 1,5 roku"