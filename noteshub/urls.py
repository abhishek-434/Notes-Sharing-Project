from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, NotesSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'notes': NotesSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('notes/', include('notes.urls')),
    path('categories/', include('categories.urls')),
    path('forum/', include('forum.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site header
admin.site.site_header = "NotesHub Administration"
admin.site.site_title = "NotesHub Admin Portal"
admin.site.index_title = "Welcome to NotesHub Admin"
