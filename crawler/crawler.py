import requests
import re

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from time import sleep
from urllib.request import urlretrieve


class AbstractCrawler(ABC):
    '''
    URL: https://dados.ufrn.br
    \nrobots.txt:
    
        User-agent: *
        Disallow: /dataset/rate/
        Disallow: /revision/
        Disallow: /dataset/*/history
        Disallow: /api/

        User-Agent: *
        Crawl-Delay: 10

    '''
    def __init__(self, docs_db):
        self.docs_db = docs_db
        
    @abstractmethod
    def crawl(self) -> None:
        pass
    

class Crawler(AbstractCrawler):
    def __init__(self, docs_db):
        super().__init__(docs_db)
        
    def crawl(self) -> None:
        for dataset_url in ['https://dados.ufrn.br/dataset/docentes', 'https://dados.ufrn.br/dataset/cursos-de-graduacao']:
            links = self.request(dataset_url)
            self.save(links)
            

    def save_file(self, filename: str, href: str) -> None:
        path = f'{self.csvs_path}{filename}'
        response = requests.get(href, verify=False)
        with open(path, 'wb') as f:
            f.write(response.content)
    
    def save(self, links) -> None:
        for link in links:
            try:
                path = f'./crawler/csvs/{link["href"].split("/")[-1]}'
                response = requests.get(link['href'], verify=False)
                with open(path, 'wb') as f:
                    f.write(response.content)
                print(f'Arquivo salvo: {path}')
            except Exception as e:
                print(f'Erro ao baixar o arquivo: {e}')
            finally:
                sleep(10) # Espera 10 segundos entre cada requisição, regra definida no robots.txt do site

    def request(self, url: str):
        html: bytes = requests.get(url).content
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        pattern = re.compile(r".*\.csv$")
        links = soup.find_all('a', href=pattern)
        return links
    
    def process(self, filename: str, documents: list[dict]):
        with open(f'{self.csvs_path}/{filename}') as file:
            reader = csv.reader(file, delimiter=';')
            keys = next(reader)
            for row in reader:
                documents.append(dict(zip(keys, row)))

