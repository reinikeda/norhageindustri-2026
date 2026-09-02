from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from pages.models import Project, Service
from products.models import Category, Product


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "pages:home",
            "pages:solutions",
            "pages:cases",
            "pages:wholesale",
            "pages:services",
            "pages:about",
            "pages:contact",
            "pages:quote",
            "pages:terms",
            "pages:privacy",
            "pages:cookies",
        ]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.filter(is_active=True)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Service.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
