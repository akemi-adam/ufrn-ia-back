from django.http import HttpResponse
from .crawler import AbstractCrawler, Crawler

def index(request):
    crawler: AbstractCrawler = Crawler(None)
    crawler.crawl()
    return HttpResponse("Arquivos salvos.")