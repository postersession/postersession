from django.contrib import admin

# Register your models here.

from .models import Conference, Poster, Author, PosterAuthor


class PosterAuthorsInline(admin.TabularInline):
    model = PosterAuthor
    extra = 1

class PosterAdmin(admin.ModelAdmin):
    search_fields = ['title', 'conference__name', 'authors__name', 'authors__email']
    inlines = (PosterAuthorsInline,)

class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'poster__title']
    inlines = (PosterAuthorsInline,)


admin.site.register(Conference)
admin.site.register(Author, AuthorAdmin)
admin.site.register(PosterAuthor)
admin.site.register(Poster, PosterAdmin)

admin.site.site_header = 'Postersession.ai Administration'
