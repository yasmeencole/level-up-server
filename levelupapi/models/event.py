from django.db import models
from pydoc import describe


class Event(models.Model):
    host = models.ForeignKey("Gamer", on_delete=models.CASCADE)
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()
    attending_gamer = models.ManyToManyField("Gamer", through="AttendingGamer", related_name="attending")
    date = models.DateField()
    time = models.TimeField()