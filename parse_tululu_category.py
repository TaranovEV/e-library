import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin, urlencode
import json


def parse_book_page(responce):
    """
    Args:
        response (requests.Response Object)
    Returns:
        Функция возвращает словарь со следующими ключами:
            'author' - Автор Книги
            'title' - Название
            'genres' - Жанр(ы)
            'comments' - Комментарии
            'image_url' - Ссылка на изображение

    """
    soup = BeautifulSoup(responce, 'lxml')
    text_header = soup.find('h1').text
    title_and_author = [el.strip() for el in text_header.split('::')]
    title, author = title_and_author
    comments_in_page = soup.find_all('div', class_='texts')
    genres = soup.find('span', class_='d_book').find_all('a')
    image_url = soup.find('div', class_='bookimage').find('img')['src']
    books_info = {
        'author': author,
        'title': title,
        'genres': [genre.text for genre in genres],
        'comments': [],
        'image_url': image_url,
    }
    if comments_in_page:
        comments = [
            comment.find('span', class_='black').text
            for comment in comments_in_page
            ]
        books_info['comments'] = comments
    return books_info


def download_image(title_url, image_url, folder='images/'):
    """Функция для скачивания изображений.
    Args:
        title_url (str): Cсылка на страницу, содержащую изображение.
        image_url (str): Ссылка на изображение.
        folder (str): Папка, куда сохранять.
    Returns:

    """

    response = requests.get(urljoin(title_url, image_url))
    response.raise_for_status()
    check_for_redirect(response)
    filename = os.path.basename(image_url)
    filename = sanitize_filename(filename)
    fpath = sanitize_filepath(os.path.join(folder, filename))
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(fpath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:

    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
        filename = sanitize_filename(''.join([filename, '.txt']))
        fpath = sanitize_filepath(os.path.join(folder, filename))
        Path(folder).mkdir(parents=True, exist_ok=True)
        with open(fpath, 'w') as file:
            file.write(response.text)
    except requests.HTTPError:
        pass


books_description = []
for page_id in range(1, 11):
    query = {'id': page_id}
    params = urlencode(query)
    download_url = f'http://tululu.org/txt.php?{params}'
    title_url = 'http://tululu.org/l55/{page_id}'.format(page_id=page_id)
    try:
        response = requests.get(title_url)
        response.raise_for_status()
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        book_links = soup.find_all('div', class_='bookimage')
        for book in book_links:
            book_page_response = (
                requests.get(urljoin(title_url, book.find('a')['href']))
            )
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
            books_info = parse_book_page(book_page_response.text)
            download_txt(download_url,
                         books_info['title'],
                         folder='books/')
            download_image(title_url,
                           books_info['image_url'],
                           folder='images/')
            books_description.append(books_info)
    except requests.HTTPError:
        pass
with open('books_description.json', 'w') as file:
    json.dump(books_description, file, ensure_ascii=False)
