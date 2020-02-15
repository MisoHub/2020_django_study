from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .models import Post, Category, Tag
from django.views.generic import ListView,DetailView,UpdateView, CreateView

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')
        # To ordering recent post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        return context

class PostDetail(DetailView):
    model = Post
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'head_image', 'category', 'tags']
    
    def form_valid(self, form):
        if self.request.user is None or self.request.user.is_anonymous:
            return redirect('/blog/')
        current_user = self.request.user
        if current_user.is_authenticated():
            form.instance.author = current_user
        else:
            return redirect('/blog/')
    
        return super(type(self),self).form_valid(form)

class PostUpdate(UpdateView):
    model = Post
    fields = ['title', 'content', 'head_image', 'category', 'tags']


class PostListByCategory(ListView):
    def get_queryset(self):
        slug = self.kwargs['slug']
        category = None if slug == '_none' else Category.objects.get(slug=slug)
        return Post.objects.filter(category=category).order_by('-created')
        # To ordering recent post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['filtered_category'] = 'No Category' if slug == '_none' else Category.objects.get(slug=slug)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        return context


class PostListByTag(ListView):
    def get_queryset(self):
        slug = self.kwargs['slug']
        tag = Tag.objects.get(slug=slug)
        return tag.post_set.order_by('-created')
        # To ordering recent post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['filtered_tag'] = Tag.objects.get(slug=slug)
        context['is_tag'] = 'TAG'
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        return context



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
