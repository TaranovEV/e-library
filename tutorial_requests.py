import requests
from pathlib import Path


NEW_DIRECTORY = './books'
URL = 'http://tululu.org/txt.php?id=32168'

Path(NEW_DIRECTORY).mkdir(parents=True, exist_ok=True)

for id in range(1, 11):
    url = 'http://tululu.org/txt.php?id={id}'.format(id=id)
    response = requests.get(url)
    response.raise_for_status()

    filename = NEW_DIRECTORY + '/' + 'id{id}.txt'.format(id=id)
    with open(filename, 'wb') as file:
        file.write(response.content)