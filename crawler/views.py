from django.http import HttpResponse
from .crawler import AbstractCrawler, Crawler
from docs.factories.documents import DocumentsFactory, QdrantFactory

def index(request):
    docs_handler: DocumentsFactory = QdrantFactory()
    crawler: AbstractCrawler = Crawler(docs_handler)
    crawler.crawl()
    return HttpResponse("Arquivos salvos.")

def saveDocs(request):
    docs_handler: DocumentsFactory = QdrantFactory()
    crawler: AbstractCrawler = Crawler(docs_handler)
    crawler.saveDocs()
    return HttpResponse("Arquivos processados.")

def testSearch(request):
    docs_handler: DocumentsFactory = QdrantFactory()
    result = docs_handler.improve_prompt('departamento de computação e tecnologia')
    return HttpResponse(f'<pre>{result}</pre>')
