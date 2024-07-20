from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    # path('posts/', views.all_blogs, name='posts'),
    # path('posts/blog-details/<int:pk>/', views.post_details, name='post_details')
]