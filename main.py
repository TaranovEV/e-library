import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filepath, sanitize_filename


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
        str: Путь до файла, куда сохранён текст.
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
            title_and_author =  [el.strip() for el in text_header.split('::')]   
            download_txt(url_for_download, title_and_author[0], folder='books/')
        except requests.HTTPError:
           pass

if __name__ in '__main__':
    main()