from django.contrib import admin
from django.utils.html import format_html_join, mark_safe

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
    #inlines = (PosterAuthorsInline,)
    readonly_fields = ['poster_list']

    def poster_list(self, instance):
        return format_html_join(
            '\n', '<p>{}</p>', ((p,) for p in instance.posters)
        )
    poster_list.short_description = "Posters"


admin.site.register(Conference)
admin.site.register(Author, AuthorAdmin)
admin.site.register(PosterAuthor)
admin.site.register(Poster, PosterAdmin)

admin.site.site_header = 'Postersession.ai Administration'
