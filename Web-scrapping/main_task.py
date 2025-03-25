import requests
from bs4 import BeautifulSoup

KEYWORDS = ['дизайн', 'фото', 'web', 'python']


def find_articles(keywords):
    url = 'https://habr.com/ru/articles/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='tm-articles-list__item')

    print(f"Найдено {len(articles)} статей на странице.")

    for article in articles:
        date_element = article.find('time')
        date = date_element.get('datetime') if date_element else "Дата не найдена"

        link = "Ссылка не найдена"
        title = "Заголовок не найден"

        title_element = article.find('h3', class_='tm-news-block-item__title')
        if title_element:
            link_element = title_element.find('a', class_='tm-news-block-item__title-link')
            if link_element:
                link = 'https://habr.com' + link_element.get('href')
                title = link_element.text.strip()

        if link == "Ссылка не найдена":
            title_element = article.find('h2', class_='tm-title tm-title_h2')
            if title_element:
                link_element = title_element.find('a', class_='tm-title__link')
                if link_element:
                    link = 'https://habr.com' + link_element.get('href')
                    title = link_element.text.strip()

        preview_text_element = article.find('div', class_='tm-article-body tm-article-body_preview')
        if preview_text_element:
            preview_text = preview_text_element.text.strip()
        else:
            snippet_element = article.find('div', class_='tm-article-snippet')
            preview_text = snippet_element.text.strip() if snippet_element else ""

        text_to_search = preview_text  # Поиск только в preview

        for keyword in keywords:
            if keyword.lower() in text_to_search.lower():
                print(f'{date} – {title} – {link}')
                break


print("--- Поиск по preview ---")
find_articles(KEYWORDS)
