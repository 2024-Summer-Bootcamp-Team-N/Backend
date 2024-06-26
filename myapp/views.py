from django.http import HttpResponse
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
    global topics
    ol = ''
    for topic in topics:
        ol += f'<li><a href="/read/{topic["id"]}">{topic["title"]}</a></li>'
    return HttpResponse(f'''
    <html>
    <body>
        <h1>Team-N 여러분, 서버에 오신것을 환영합니다!!!</h1>
        <ol>
            {ol}
        <ol>
        <h1>우리팀 주제는?</h1>
        화이팅합시다...
    <body>
    <html>
    ''')

def create(request):
    return HttpResponse("created!!!")

def read(request, id):
    return HttpResponse("하이퍼링크 서버경로"+id)