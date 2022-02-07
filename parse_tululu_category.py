import argparse
import json
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin, urlencode


def find_number_last_page(url):
    """Функция поиска последней страницы.
    Args:
        url - url адрес страницы
    Return:
        номер последней страницы

    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    last_page_selector = 'a.npage'
    return int(soup.select(last_page_selector)[-1].text)


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
    fpath = sanitize_filepath(
        os.path.join(folder, filename), platform='auto'
    )
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
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = sanitize_filename(f'{filename}.txt')
    fpath = sanitize_filepath(
        os.path.join(folder, filename), platform='auto'
    )
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(fpath, 'w') as file:
        file.write(response.text)


def main():
    url = 'http://tululu.org/l55/{page_number}'.format(page_number='')
    last_page_number = find_number_last_page(url)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page',
                        help='номер стартовой страницы парсера',
                        type=int,
                        default=last_page_number - 1)
    parser.add_argument('--end_page',
                        help='номер "конечной" страницы парсера',
                        type=int,
                        default=last_page_number)
    parser.add_argument('--dest_folder',
                        help='''путь к каталогу с результатами парсинга:
                        картинкам, книгам, JSON''',
                        type=Path,
                        default=os.getcwd())
    parser.add_argument('--skip_imgs',
                        help='не скачивать картинки',
                        action='store_true',
                        default=False)
    parser.add_argument('--skip_txt',
                        help='не скачивать книги',
                        action='store_true',
                        default=False)
    parser.add_argument('--json_path',
                        help='указать свой путь к *.json файлу с результатами',
                        type=Path,
                        default=os.getcwd())
    args = parser.parse_args()
    assert_message = 'Аргумент end_page должен быть больше чем start_page'
    assert args.end_page >= args.start_page, assert_message
    books_description = []
    for page_number in range(args.start_page, args.end_page + 1):
        query = {'id': page_number}
        params = urlencode(query)
        download_url = f'http://tululu.org/txt.php?{params}'
        page_url = url.format(page_number=page_number)
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_elements_selector = 'div.bookimage'
            books_page_elements = soup.select(book_elements_selector)
            for book in books_page_elements:
                book_page_response = (
                    requests.get(
                        urljoin(page_url,
                                book.select_one('a')['href'])
                    )
                )
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response)
                books_info = parse_book_page(book_page_response.text)
                if not args.skip_txt:
                    download_txt(download_url,
                                 books_info['title'],
                                 folder=os.path.join(args.dest_folder,
                                                     'books/'))
                if not args.skip_imgs:
                    download_image(page_url,
                                   books_info['image_url'],
                                   folder=os.path.join(args.dest_folder,
                                                       'images/'))
                books_description.append(books_info)
        except requests.HTTPError:
            pass
    json_path = os.path.join(args.json_path, 'books_description.json')
    json_path = sanitize_filepath(json_path, platform='auto')
    with open(json_path, 'w') as file:
        json.dump(books_description, file, ensure_ascii=False)


if __name__ in '__main__':
    main()
