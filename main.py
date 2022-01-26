import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename
from urllib.parse import urljoin


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
    filename = sanitize_filename(image_name)
    fpath = os.path.join(folder, filename)
    fpath = sanitize_filepath(fpath)
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
    filename = sanitize_filename(''.join([filename, '.txt']))
    fpath = os.path.join(folder, filename)
    fpath = sanitize_filepath(fpath)
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(fpath, 'wb') as file:
        file.write(response.content)


def main():
    for id in range(1, 11):
        url_for_download = 'http://tululu.org/txt.php?id={id}'.format(id=id)
        url_for_title = 'http://tululu.org/b{id}/'.format(id=id)
        try:
            response_for_title = requests.get(url_for_title)
            response_for_title.raise_for_status()
            check_for_redirect(response_for_title)
            soup = BeautifulSoup(response_for_title.text, 'lxml')
            text_header = soup.find('h1').text
            title_and_author = [el.strip() for el in text_header.split('::')]
            comments = soup.find_all('div', class_='texts')
            print(title_and_author[0], '\n')
            if comments:
                for comment in comments:
                    print(comment.find('span', class_='black').text)
            image = soup.find('div', class_='bookimage').find('img')['src']
            download_txt(url_for_download,
                         title_and_author[0],
                         folder='books/')
            download_image(url_for_title,
                           image,
                           folder='images/')
        except requests.HTTPError:
            pass


if __name__ in '__main__':
    main()
