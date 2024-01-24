import requests
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
import csv
import json


data_path = Path('.')/'data'


if not data_path.exists():
    data_path.mkdir()

url = 'https://bestkino.kz'
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0"
}

req = requests.get(url=url, headers=HEADERS)
src = req.text

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(src)


with open('index.html', encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

all_categories = soup.find('ul', class_='nav-sidebar').find_all('a')

all_categories_dict = {}
for item in all_categories:
    category_title = item.text
    category_ref = item.get('href')
    all_categories_dict[category_title] = url + category_ref


with open('categories_dict.json', 'w', encoding='utf-8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open('categories_dict.json', encoding='utf-8') as file:
    all_categories_dict = json.load(file)


initial_count = int(len(all_categories_dict.items()) - 2)
for category, catefory_ref in all_categories_dict.items():

    print(f"Категория фильмов {category} загружается...")

    html_text = requests.get(catefory_ref).text

    soup = BeautifulSoup(html_text, 'lxml')

    content = soup.find_all(class_='shortf')
    if content:
        with open(f"{data_path}/{category}.csv", 'w', encoding='utf-8') as file:
            writter = csv.writer(file)
            writter.writerow(
                ('Название фильма', 'Название по английски', 'Ссылка на фильм'))
        for item in content:
            film_name_russian = item.find('b').text
            film_name_english = item.find('small').text
            film_ref = item.find('a').get('href')

            with open(f"{data_path}/{category}.csv", 'a', encoding='utf-8') as file:
                writter = csv.writer(file)
                writter.writerow((
                    film_name_russian, film_name_english, film_ref
                ))
        if soup.find('div', class_='pages-numbers') is not None:
            pagination = [el.get('href') for el in soup.find(
                'div', class_='pages-numbers').find_all('a')]

            list_of_pages = soup.find(class_='pages-numbers').find_all('a')

            for ref in pagination:
                html_text = requests.get(ref).text
                soup = BeautifulSoup(html_text, 'lxml')
                content = soup.find_all(class_='shortf')
                for item in content:
                    film_name_russian = item.find('b').text
                    film_name_english = item.find('small').text
                    film_ref = item.find('a').get('href')

                    with open(f"{data_path}/{category}.csv", 'a', encoding='utf-8') as file:
                        writter = csv.writer(file)
                        writter.writerow((
                            film_name_russian, film_name_english, film_ref
                        ))
                sleep(1)

            if initial_count == 0:
                print('Все фильмы загружены!')
        initial_count -= 1
        print(f"Категория {category} загружена! Осталось категорий {
            initial_count}")
