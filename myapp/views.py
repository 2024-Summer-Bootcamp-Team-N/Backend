from django.http import HttpResponse
from django.shortcuts import render

topics = [
    {'id':1, 'title': '수하', 'body':'Routing is ..'},
    {'id':2, 'title': '민기', 'body':'Views are ..'},
    {'id':3, 'title': '민균', 'body':'Models are ..'},
    {'id':4, 'title': '혁진', 'body':'Functions are ..'},
    {'id':5, 'title': '수민', 'body':'Classes are ..'},
    {'id':6, 'title': '종완', 'body':'Methods are ..'},
    {'id':7, 'title': '재준', 'body':'Variables are ..'},
]
def index(request):
    return render(request, 'index.html', {'topics': topics})

def create(request):
    return HttpResponse("created!!!")

def read(request, id):
    return HttpResponse("하이퍼링크 서버경로"+id)