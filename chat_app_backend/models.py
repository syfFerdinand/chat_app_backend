from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Message(models.Model):
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_message')
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='updated_message')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def undelete(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.content
