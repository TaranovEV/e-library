import argparse
from email import message
import json
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin, urlencode


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
    header_selector = 'h1'
    text_header = soup.select_one(header_selector).text
    title_and_author = [el.strip() for el in text_header.split('::')]
    title, author = title_and_author
    comments_in_page_selector = 'div.texts'
    comments_in_page = soup.select(comments_in_page_selector)
    genres_selector = 'span.d_book a'
    genres = soup.select(genres_selector)
    image_url_selector = 'div.bookimage img'
    image_url = soup.select_one(image_url_selector)['src']
    books_info = {
        'author': author,
        'title': title,
        'genres': [genre.text for genre in genres],
        'comments': [],
        'image_url': image_url,
    }
    if comments_in_page:
        comments = [
            comment.select_one('span.black').text
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page',
                        help='номер стартовой страницы парсера',
                        type=int,
                        default=700)
    parser.add_argument('--end_page',
                        help='номер "конечной" страницы парсера',
                        type=int,
                        default=702)
    args = parser.parse_args()
    assert_message = 'Аргумент end_page должен быть больше чем start_page'
    assert args.end_page >= args.start_page, assert_message
    books_description = []
    for page_number in range(args.start_page, args.end_page):
        query = {'id': page_number}
        params = urlencode(query)
        download_url = f'http://tululu.org/txt.php?{params}'
        title_url = (
            'http://tululu.org/l55/{page_number}'
            .format(page_number=page_number)
        )
        try:
            response = requests.get(title_url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_links_selector = 'div.bookimage'
            book_links = soup.select(book_links_selector)
            for book in book_links:
                book_page_response = (
                    requests.get(
                        urljoin(title_url,
                                book.select_one('a')['href'])
                    )
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


if __name__ in '__main__':
    main()
