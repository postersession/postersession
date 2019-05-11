from django.db import models
from datetime import date
from django.utils import timezone


class Conference(models.Model):
    name = models.CharField(max_length=256)
    date_from = models.DateField(default=date.today)
    date_to = models.DateField(default=date.today)
    location = models.CharField(max_length=256, blank=True)
    web = models.URLField(max_length=256, blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True, blank=True)

    def __str__(self):
        return self.name + ' <' + self.email + '>'


class Poster(models.Model):
    title = models.CharField(max_length=256)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateField('date published', default=date.today)
    authors = models.ManyToManyField(Author)
    access_key = models.CharField(max_length=256, unique=True)
    file_id = models.CharField(max_length=80, blank=True)
    pdf = models.FileField(upload_to='pdf/')
    external_id = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' (' + self.conference.name + ')'

