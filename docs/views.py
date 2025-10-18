from django.shortcuts import render

from django.http import HttpResponse
from docs.factories.documents import DocumentsFactory, QdrantFactory
from docs.strategies.llm import PromptResponseStrategy, NvidiaResponse

def index(request):
    response_strategy: PromptResponseStrategy = NvidiaResponse()
    docs_handler: DocumentsFactory = QdrantFactory()
    user_prompt: str = request.GET.get('user_prompt')
    final_prompt: str = docs_handler.improve_prompt(user_prompt)
    response_strategy.response(final_prompt)
    return HttpResponse('OK')