# Скрипт для парсинга онлайн библиотеки


## Описание функций из main.py

- find_number_last_page:  
    Функция поиска номера последней страницы.    

- parse_book_page:  
  Функция принимает контент страницы,  
  возвращает словарь с информацией по книге 
            
- download_image:  
    Функция для скачивания изображений.    
        
- check_for_redirect:  
Поднимает исключение при отстутсвии страницы

- download_txt:  
    Функция для скачивания текстовых файлов. 
 
## Запуск

- Скачайте код
- Установите зависимости командой:
  ```
  pip install -r requirements.txt
   ```
- Запустите скрипт командой:
  ```
  python parse_tululu_category.py
  ```
  В этом случае скрипт запустится с аргументоми по умолчанию:  
  `--start_id = 1`  
  `--end_id = 11`  
  `--dest_folder = текущая директория, со скриптом`  
  `--skip_imgs = False`  
  `--skip_txt = False`  
  `--json_path = текущая директория, со скриптом`  
  
  Аргументы скрипта:  
  
  `--start_id` - (*type:int*) номер стартовой страницы парсера  
  
  `--end_id` - (*type:int*) номер "конечной" страницы парсера 
  
  `--dest_folder` - (*type:Path,str*) путь к каталогу с результатами парсинга: картинкам, книгам, JSON.  
  *Например: "C:\Users\User\my_doc\e-library"*  
  
  `--skip_imgs` - (*type:bool*) не скачивать картинки, возможные значения True или False   
  
  `--skip_txt` - (*type:bool*) не скачивать книги, возможные значения True или False   
  
  `--json_path` - (*type:Path,str*) указать свой путь к файлу *books_description.json* с результатами  
  Название файла json неизменно    
  *Например: "C:\Users\User\my_doc\e-library"* 
  
