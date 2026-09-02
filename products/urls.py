from django.urls import path
from django.views.generic import RedirectView

from .views import ProductDetailView

app_name = "products"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(pattern_name="pages:solutions", permanent=False),
        name="index",
    ),
    path("<slug:sku>/", ProductDetailView.as_view(), name="detail"),
]
