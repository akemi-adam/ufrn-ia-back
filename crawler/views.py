from django.http import HttpResponse
from .crawler import AbstractCrawler, Crawler
from docs.factories.documents import DocumentsFactory, QdrantFactory

def run_crawler(request):
    docs_handler = QdrantFactory()
    crawler = Crawler(docs_handler)
    crawler.crawl()
    return HttpResponse("Arquivos salvos/processados")

def testSearch(request):
    docs_handler: DocumentsFactory = QdrantFactory()
    result = docs_handler.improve_prompt('departamento de computação e tecnologia')
    return HttpResponse(f'<pre>{result}</pre>')
