from django.db import models
from datetime import date
from django.utils import timezone
from validatedfile.fields import ValidatedFileField

from .tasks import generate_preview



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
    email = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name + ' <' + str(self.email) + '>'


class Poster(models.Model):
    title = models.CharField(max_length=256)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateField('date published', default=date.today)
    authors = models.ManyToManyField(Author)
    access_key = models.CharField(max_length=256, unique=True)
    external_id = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=False)
    preview_small = models.ImageField(blank=True, upload_to='jpeg/')
    preview_large = models.ImageField(blank=True, upload_to='jpeg/')
    pdf = ValidatedFileField(
                    blank=True,
                    upload_to='pdf/',
                    max_upload_size=10240000,
                    content_types=['application/pdf'])

    def generate_preview(self):
        generate_preview(self)

    def __str__(self):
        return self.title + ' (' + self.conference.name + ')'

