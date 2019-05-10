from django.contrib import admin

# Register your models here.

from .models import Conference, Poster, Author

admin.site.register(Conference)
admin.site.register(Author)
admin.site.register(Poster)
