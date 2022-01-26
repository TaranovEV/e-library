import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin
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
        comments = []
        for comment in comments_in_page:
            comments.append(comment.find('span', class_='black').text)
        books_info['comments'] = comments

    print(books_info)
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
                        default=1)
    parser.add_argument('end_id',
                        help='id "конечной" страницы парсера',
                        type=int,
                        default=11)
    args = parser.parse_args()
    for id in range(args.start_id, args.end_id):
        url_for_download = 'http://tululu.org/txt.php?id={id}'.format(id=id)
        url_for_title = 'http://tululu.org/b{id}/'.format(id=id)
        try:
            response_for_title = requests.get(url_for_title)
            response_for_title.raise_for_status()
            check_for_redirect(response_for_title)
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            books_info = parse_book_page(soup)
            image = soup.find('div', class_='bookimage').find('img')['src']
            download_txt(url_for_download,
                         books_info['title'],
                         folder='books/')
            download_image(url_for_title,
                           image,
                           folder='images/')
        except requests.HTTPError:
            pass


if __name__ in '__main__':
    main()
