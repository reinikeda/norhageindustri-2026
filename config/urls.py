from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import (
    CategorySitemap,
    ProductSitemap,
    ProjectSitemap,
    ServiceSitemap,
    StaticSitemap,
)
from core.views import robots_txt

admin.site.site_header = "Norhage Industri"
admin.site.site_title = "Norhage Industri admin"
admin.site.index_title = "Site administration"

sitemaps = {
    "static": StaticSitemap,
    "categories": CategorySitemap,
    "products": ProductSitemap,
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
}

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("products/", include("products.urls")),
    path("quote/", include("quotes.urls")),
    path("", include("pages.urls")),
]

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
