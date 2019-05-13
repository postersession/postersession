from django.db import models
from datetime import date
from django.utils import timezone
from constrainedfilefield.fields import ConstrainedFileField
from unique_upload import unique_upload

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
    authors = models.ManyToManyField(Author, through='PosterAuthor')
    access_key = models.CharField(max_length=256, unique=True)
    external_id = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=False)
    preview_small = models.ImageField(blank=True, upload_to=unique_upload)
    preview_large = models.ImageField(blank=True, upload_to=unique_upload)
    pdf = ConstrainedFileField(
                    blank=True,
                    upload_to=unique_upload,
                    max_upload_size=10240000,
                    content_types=['application/pdf'])

    def author_list(self):
        return [obj.author for obj in PosterAuthor.objects.filter(poster=self).order_by('position')]

    def generate_preview(self):
        generate_preview(self)

    def __str__(self):
        return self.title + ' (' + self.conference.name + ')'


class PosterAuthor(models.Model):
    ''' represent author order '''
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        ''' automatically increment position on creation '''
        if not self.pk: # object has not been saved yet
            max_position = PosterAuthor.objects.filter(poster=self.poster).order_by('-position')
            if max_position.exists():
                self.position = max_position.all()[0].position + 1
        super(PosterAuthor, self).save(*args, **kwargs)

    class Meta:
        ordering = ['position']


