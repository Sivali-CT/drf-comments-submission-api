from django.db import models

class Comment(models.Model):
    post_id = models.IntegerField()
    text = models.TextField()
    username = models.CharField(max_length=16, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        return f"{self.username}"