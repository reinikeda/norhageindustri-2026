from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Norhage Industri"
admin.site.site_title = "Norhage Industri admin"
admin.site.index_title = "Site administration"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("products/", include("products.urls")),
    path("", include("pages.urls")),
]

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
