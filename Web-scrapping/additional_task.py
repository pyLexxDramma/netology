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

        if link != "Ссылка не найдена":
            try:
                article_response = requests.get(link)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                full_text_element = article_soup.find('div', class_='tm-article-body')
                full_text = full_text_element.text.strip() if full_text_element else ""
                text_to_search = full_text
            except requests.exceptions.RequestException:
                text_to_search = ""

            for keyword in keywords:
                if keyword.lower() in text_to_search.lower():
                    print(f"Найдено ключевое слово '{keyword}' в тексте.")
                    print(f'{date} – {title} – {link}')
                    break
        else:
            print("Ссылка не найдена для этой статьи.")


if __name__ == "__main__":
    print("--- Поиск по полному тексту статьи ---")
    find_articles(KEYWORDS)
