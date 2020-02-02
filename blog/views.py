from django.shortcuts import render
from .models import Post

from django.views.generic import ListView,DetailView



class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')
        # To ordering recent post

class PostDetail(DetailView):
    model = Post
# Create your views here.

# def  post_detail(request, pk):
#     detail_post = Post.objects.get(pk=pk)
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'detail_post' : detail_post,
#         }
#     )


# def index(request):
#
#     posts = Post.objects.all()
#
#     return render(
#         request,
#         'blog/index.html',   # at blog/templates/blog/index.html
#          {
#             'posts' : posts,
#              'a_plus_b' : 1+3 ,
#          }
#     )
