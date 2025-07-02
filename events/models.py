from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    max_capacity = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Attendee(models.Model):
    event = models.ForeignKey(Event, related_name='attendees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    class Meta:
        unique_together = ('event', 'email')

