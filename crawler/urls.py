from django.urls import path

from . import views

urlpatterns = [
    path('', views.run_crawler, name='run-crawler'),
    path('search', views.testSearch, name='search')
]