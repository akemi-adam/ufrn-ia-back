import csv
import requests
import re

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from time import sleep
from os import listdir, remove
from os.path import isfile, join

from docs.factories.documents import DocumentsFactory

# Tempo em segundos entre cada requisição
# Regra definida no robots.txt do site
ROBOTS_WAIT_TIME = 10

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
    def __init__(self, docs_handler: DocumentsFactory):
        self.docs_handler: DocumentsFactory = docs_handler
        
    @abstractmethod
    def crawl(self) -> None:
        pass

    @abstractmethod
    def saveDocs(self) -> None:
        pass
    

class Crawler(AbstractCrawler):
    csvs_path: str = './crawler/csvs/'

    def __init__(self, docs_handler: DocumentsFactory):
        super().__init__(docs_handler)
        
    def crawl(self) -> None:
        # Substituir por uma lista de URLs a serem crawleadas que vem do banco de dados
        # Aqui tem que verificar também se a coleção já existe/comparar a data da última atualização no site com a data do último crawl/scraping 
        for dataset_url in ['https://dados.ufrn.br/dataset/docentes', 'https://dados.ufrn.br/dataset/cursos-de-graduacao']:
            links = self.request(dataset_url)
            self.save(links)
            sleep(ROBOTS_WAIT_TIME)

    def save_file(self, filename: str, href: str) -> None:
        path = f'{self.csvs_path}{filename}'
        response = requests.get(href, verify=False)
        with open(path, 'wb') as f:
            f.write(response.content)
    
    def save(self, links) -> None:
        for link in links:
            try:
                href: str = link["href"]
                filename: str = href.split("/")[-1]
                self.save_file(filename, href)
                self.docs_handler.create_storage(filename)
            except Exception as e:
                print(f'Erro ao baixar o arquivo: {e}')
            finally:
                sleep(ROBOTS_WAIT_TIME)

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

    def list_csvs(self) -> list[str]:
        return [x for x in listdir(self.csvs_path) if isfile(join(self.csvs_path, x))]

    def saveDocs(self) -> None:
        # Antes de salvar, tem que deletar os dados antigos no banco de dados (qdrant)
        # Se quiser fazer melhor, na hora de fazer o web scraping, você pode comparar a data de atualização do dataset no site com a data do último crawl/scraping, e aí só pegar os CSVs novos, se houver
        # Com isso não precisaria apagar os dados antigos
        for filename in self.list_csvs():
            documents: list[dict] = []
            self.process(filename, documents)
            self.docs_handler.save(documents, filename)
            remove(f'{self.csvs_path}/{filename}')
