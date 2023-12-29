from django.urls import path
from .views import CommentList, CommentByPostIdView

urlpatterns = [
    path('lists/', CommentList.as_view(), name='comment-list'),
    path('lists/<int:post_id>/', CommentByPostIdView.as_view(), name='comment-by-post-id')

]