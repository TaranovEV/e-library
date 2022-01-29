import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin, urlencode
import argparse


def parse_book_page(content):
    """
    Args:
        content (BeautifulSoup object) - контент страницы
    Returns:
        Функция возвращает словарь со следующими ключами:
            'author' - Автор Книги
            'title' - Название
            'genres' - Жанр(ы)
            'comments' - Комментарии

    """
    text_header = content.find('h1').text
    title_and_author = [el.strip() for el in text_header.split('::')]
    comments_in_page = content.find_all('div', class_='texts')
    genres = content.find('span', class_='d_book').find_all('a')
    books_info = {
        'author': title_and_author[1],
        'title': title_and_author[0],
        'genres': [genre.text for genre in genres],
        'comments': []
    }
    if comments_in_page:
        comments = [
            comment.find('span', class_='black').text
            for comment in comments_in_page
            ]
        books_info['comments'] = comments

    return books_info


def download_image(url, image, folder='images/'):
    """Функция для скачивания изображений.
    Args:
        url (str): Cсылка на страницу, содержащую изображение.
        image (str): Ссылка на изображение.
        folder (str): Папка, куда сохранять.
    Returns:

    """
    image_name = os.path.basename(image)
    response = requests.get(urljoin(url, image))
    fpath = collect_path(folder, image_name, txt=False)
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(fpath, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def collect_path(folder, filename_in_page, txt=True):
    """
    Функция собирает путь к сохраняемому файлу
    Args:
        folder (str): Название создаваемой папки
        filename_in_page (str): Название файла на странице

    Returns (str):
        Путь к сохраняемому файлу
    """
    if txt:
        filename = sanitize_filename(''.join([filename_in_page, '.txt']))
    else:
        filename = sanitize_filename(filename_in_page)
    fpath = os.path.join(folder, filename)

    return sanitize_filepath(fpath)


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:

    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    fpath = collect_path(folder, filename, txt=True)
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(fpath, 'wb') as file:
        file.write(response.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id',
                        help='id стартовой страницы парсера',
                        type=int,
                        nargs='?',
                        default=1)
    parser.add_argument('end_id',
                        help='id "конечной" страницы парсера',
                        type=int,
                        nargs='?',
                        default=11)
    args = parser.parse_args()
    for id_page in range(args.start_id, args.end_id):
        query = {'id': id_page}
        params = urlencode(query)
        download_url = f'http://tululu.org/txt.php?{params}'
        title_url = f'http://tululu.org/b{id_page}/'
        try:
            title_response = requests.get(title_url)
            title_response.raise_for_status()
            check_for_redirect(title_response)
            soup = BeautifulSoup(title_response.text, 'lxml')
            books_info = parse_book_page(soup)
            image = soup.find('div', class_='bookimage').find('img')['src']
            download_txt(download_url,
                         books_info['title'],
                         folder='books/')
            download_image(title_url,
                           image,
                           folder='images/')
        except requests.HTTPError:
            pass


if __name__ in '__main__':
    main()
