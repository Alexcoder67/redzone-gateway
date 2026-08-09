from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events', null=True, blank = True)
    max_attendees = models.IntegerField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title}"

class Waitlist(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE, related_name='waitlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waitlist')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
            unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title}"
