from rest_framework import generics
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny] 
    ordering = ['-created_at'] 

    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        serializer.save(post_id=post_id)

class CommentByPostIdView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny] 
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

