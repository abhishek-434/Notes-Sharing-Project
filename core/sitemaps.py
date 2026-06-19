from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from notes.models import Note


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact', 'notes:list', 'forum:list', 'categories:list']

    def location(self, item):
        return reverse(item)


class NotesSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Note.objects.filter(status='approved')

    def lastmod(self, obj):
        return obj.updated_at
