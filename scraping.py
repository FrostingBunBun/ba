import requests
from bs4 import BeautifulSoup

def shorten_string(s, max_length=20):
    """Shorten the string to a maximum length, adding '...' if it's too long."""
    if len(s) > max_length:
        return s[:max_length] + "..."
    return s

def extract_news_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Successfully fetched the content from {url}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    news_blocks = soup.find_all('div', class_='e2eMLotm')

    if not news_blocks:
        print("No news blocks found!")
        return

    all_news = []

    for block in news_blocks:

        headline_tag = block.find('h2')
        headline = headline_tag.get_text() if headline_tag else "No headline found"

        link_tag = block.find('a', href=True)
        link = link_tag['href'] if link_tag else "No URL found"
        if link.startswith('/'):
            link = 'https://wiadomosci.wp.pl' + link

        img_tag = block.find('img', src=True)
        img_url = img_tag['src'] if img_tag else "No image found"
        news_item = [headline, link, img_url]
        
        all_news.append(news_item)

    return all_news

# temp
url = "https://wiadomosci.wp.pl/polska"
news_list = extract_news_from_url(url)


if news_list:
    print("\nExtracted News:")
    for news_item in news_list:

        headline, link, img_url = news_item
        print(f"Title: {shorten_string(headline, max_length=999)}")
        print(f"Link: {shorten_string(link, max_length=30)}")
        print(f"Image: {shorten_string(img_url, max_length=30)}")
        print()
