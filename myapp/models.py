from django.contrib.auth.models import User
from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_notes')
    shared_with = models.ManyToManyField(User, related_name='shared_notes', blank=True)
    
    def __str__(self) -> str:
        return self.title

class NoteHistory(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='history')
    line_numbers = models.CharField(max_length=100)  # Comma-separated line numbers
    old_content = models.TextField(blank=True, null=True)
    new_content = models.TextField(blank=True, null=True)
    operation = models.CharField(max_length=10, choices=(
        ('add', 'Addition'),
        ('update', 'Update'),
        ('delete', 'Deletion'),
    ))
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
 