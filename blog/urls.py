"""django_study URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.PostList.as_view()),  # ~/blog/
    path('<int:pk>/', views.PostDetail.as_view()),  # ~/blog/pk
    path('<int:pk>/new_comment', views.new_comment),  # ~/blog/pk
    path('delete_comment/<int:pk>', views.CommentDelete.as_view()), # class based view test
    # path('delete_comment/<int:pk>', views.delete_comment),  # ~/blog/pk
    path('create/', views.PostCreate.as_view()),
    path('<int:pk>/update/', views.PostUpdate.as_view()),  # ~/blog/pk/update/
    path('category/<str:slug>/', views.PostListByCategory.as_view()),
    path('tag/<str:slug>/', views.PostListByTag.as_view()),



    # path('<int:pk>/', views.post_detail),
    # path('',  views.index), # ~/blog/
]
