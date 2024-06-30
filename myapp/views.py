from django.http import HttpResponse
from django.shortcuts import render
<<<<<<< Updated upstream
=======
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from .models import Post
from .serializers import PostSerializer
import os
>>>>>>> Stashed changes

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
    context = {
        'topics': topics,
        'naver_map_api_key': os.getenv('NAVER_MAP_API_KEY')
    }
    return render(request, 'index.html', context)

def create(request):
    return HttpResponse("created!!!")

def read(request, id):
<<<<<<< Updated upstream
    return HttpResponse("하이퍼링크 서버경로"+id)
=======
    return HttpResponse("하이퍼링크 서버경로" + str(id))

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=['get'])
    def custom_action(self, request, pk=None):
        post = self.get_object()
        return Response({'custom': 'action'})

class PostListCreateAPIView(APIView):
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
>>>>>>> Stashed changes
