from django.db import models

# Create your models here.

from django.db import models



class Conference(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name + ' <' + self.email + '>'


class Poster(models.Model):
    title = models.CharField(max_length=256)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')
    authors = models.ManyToManyField(Author)

    def __str__(self):
        return self.title + ' (' + self.conference.name + ')'
