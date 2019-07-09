from django.db import models
from datetime import date
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from constrainedfilefield.fields import ConstrainedFileField
from unique_upload import unique_upload
from .tasks import generate_preview
from .utils.slugify import unique_slugify


class Conference(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=40, unique=True)
    date_from = models.DateField(default=date.today)
    date_to = models.DateField(default=date.today)
    location = models.CharField(max_length=256, blank=True)
    web = models.URLField(max_length=256, blank=True)
    link_url = models.URLField(max_length=256, blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name + ' <' + str(self.email) + '>'


class AuthorList:
    ''' utility class representing a list of authors '''
    def __init__(self, q):
        self.q = q
        self.authors = [obj.author for obj in q]

    def __len__(self):
        return self.authors.__len__()

    def __iter__(self):
        return self.authors.__iter__()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return AuthorList(self.q[item])
        else:
            return self.authors[item]

    def __str__(self):
        ''' formatted author list '''
        names = [a.name for a in self.authors]
        if len(self) == 0:
            return '<no authors>'
        elif len(self) == 1:
            return names[0]
        elif len(self) == 2:
            return names[0] + ' and ' + names[1]
        else: # > 1
            return ', '.join(names[:-1]) + ', and ' + names[-1]


class Poster(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=40, unique=True, blank=True)
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
                    max_upload_size=16777216,
                    content_types=['application/pdf'])

    def generate_preview(self):
        generate_preview(self)

    def save(self, *args, **kwargs):
        if not self.pk: # only create slug the first time the object is saved
            unique_slugify(self, self.title)
        super(Poster, self).save(*args, **kwargs)

    @property
    def author_list(self):
        return AuthorList(PosterAuthor.objects.filter(poster=self).order_by('position'))

    @property
    def first_author(self):
        poster_author = PosterAuthor.objects.filter(poster=self).order_by('position').first()
        return getattr(poster_author, 'author', Author(name='<no author>'))

    @property
    def num_authors(self):
        return PosterAuthor.objects.filter(poster=self).count()

    @property
    def ref_short(self):
        ''' poster title and first author '''
        etal = 'et al.' if self.num_authors > 1 else ''
        return ' '.join([self.title, 'by', self.first_author.name, etal])

    @property
    def ref_long(self):
        ''' poster title, all authors, conference name '''
        return ' '.join([self.title + '.', str(self.author_list), '(' + self.conference.name + ')'])

    @property
    def ext_url(self):
        ''' link to external paper '''
        eid = self.external_id.split('/')[-1]
        url = self.conference.link_url
        if not eid or not url:
            return None
        return url.format(id=eid)

    def get_absolute_url(self):
        return reverse('detail', args=[self.slug])

    def __str__(self):
        return self.ref_short + ' (' + str(self.conference.name) + ')'


class PosterAuthor(models.Model):
    ''' represent author order '''
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    exclude = models.BooleanField(default=False)
    email_sent = models.DateTimeField(blank=True, null=True)

    @property
    def name(self):
        return self.author.name

    def save(self, *args, **kwargs):
        ''' automatically increment position on creation '''
        if not self.pk: # object has not been saved yet
            max_position = PosterAuthor.objects.filter(poster=self.poster).order_by('-position').first()
            if max_position is not None:
                self.position = max_position.position + 1
        super(PosterAuthor, self).save(*args, **kwargs)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return str(self.author) + ' @ ' + str(self.poster)

