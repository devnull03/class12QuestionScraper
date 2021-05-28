import sys
from typing import Dict, KeysView, List
import requests
from bs4 import BeautifulSoup
import os
import webbrowser
import json
try:
    from rich import print
except ModuleNotFoundError:
    pass

try:
    with open('urls.json', 'r') as urls_file:
        JSON_DATA: Dict[str, str] = json.loads(urls_file.read())
except FileNotFoundError:
    print("Urls file not found")
    sys.exit()

ARTICLE_FOLDER: str = 'articles_html'
if ARTICLE_FOLDER not in os.listdir():
    os.mkdir(ARTICLE_FOLDER)


class FetchQuestions:
    RENDERING_SCRIPT: str = '''
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    '''
    INDEX_PAGE_START: str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Index</title>
    </head>
    <body>
        <h1>Index</h1>
        <ul>
    """
    INDEX_PAGE_MIDDLE: str = ""
    INDEX_PAGE_END: str = """
        </ul>
    </body>
    </html>
    """
    SUBJECTS: KeysView[str] = JSON_DATA.keys()

    def __init__(self, subject_name: str) -> None:
        if subject_name not in self.SUBJECTS:
            raise ValueError("Invalid Subject")
        self.subject_name: str = subject_name
        self.base_url: str = JSON_DATA[self.subject_name]
        self.links: List[str] = self.generate_urls(self.base_url)
        self.files: List[str] = []

        self.fetch_pages()

    @staticmethod
    def generate_urls(base_url: str) -> List[str]:
        links: List[str] = [
            base_url.replace('$', str(i)) for i in range(1, 17)
        ]
        print(links)
        return links

    def fetch_pages(self) -> None:
        folder: str = f"{ARTICLE_FOLDER}/{self.subject_name}"
        if self.subject_name not in os.listdir(ARTICLE_FOLDER):
            os.mkdir(folder)

        for link in self.links:
            name: str = '-'.join(link.split('/')[-1].split('-')[5:])
            print(name.__repr__())
            self.files.append(name)

            page: str = requests.get(link).content.decode('UTF-8')
            page_parsed: BeautifulSoup = BeautifulSoup(page, 'html.parser')
            thing: str = self.RENDERING_SCRIPT + \
                page_parsed.find(class_='entry-content').__str__()

            with open(f'{folder}/{name}.html', 'wb') as file:
                file.write(thing.encode('UTF-8'))

        self.create_local_index()

    def create_local_index(self) -> None:
        for page in self.files:
            self.INDEX_PAGE_MIDDLE += f'        <li><a href="./{self.subject_name}/{page}.html">{page}</a></li>\n'

        index_page = self.INDEX_PAGE_START + self.INDEX_PAGE_MIDDLE + self.INDEX_PAGE_END

        index_file_name: str = f'{self.subject_name}_index.html'
        with open(f"{ARTICLE_FOLDER}/{index_file_name}", 'wb') as file:
            file.write(index_page.encode('UTF-8'))

    @classmethod
    def create_global_index(cls) -> None:
        listdir = filter(
            lambda _: _.endswith('.html'), os.listdir(ARTICLE_FOLDER)
        )
        files: List[str] = list(map(
            lambda _:_.rstrip('_index.html'), listdir
        ))
        for page in files:
            cls.INDEX_PAGE_MIDDLE += f'        <li><a href="./{ARTICLE_FOLDER}/{page}_index.html">{page}</a></li>\n'

        index_page = cls.INDEX_PAGE_START + cls.INDEX_PAGE_MIDDLE + cls.INDEX_PAGE_END

        index_file_name: str = 'index.html'
        with open(f"{index_file_name}", 'wb') as file:
            file.write(index_page.encode('UTF-8'))




FetchQuestions('physics')
FetchQuestions('chemistry')

FetchQuestions.create_global_index()