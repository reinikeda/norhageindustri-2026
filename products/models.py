from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    class Group(models.TextChoices):
        INDUSTRY = "industry", "By industry"
        MATERIAL = "material", "By material"
        SYSTEM = "system", "By system"
        OTHER = "other", "Other"

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    group = models.CharField(max_length=20, choices=Group.choices, default=Group.OTHER)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["group", "sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        if self.parent_id:
            return f"{self.get_group_display()} / {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pages:solution_topic", kwargs={"group": self.group, "slug": self.slug})


class Product(models.Model):
    sku = models.CharField("SKU", max_length=64, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    categories = models.ManyToManyField(
        Category,
        related_name="products",
        blank=True,
        help_text="A product can belong to several subcategories (industry, material, and system).",
    )
    short_description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    technical_text = models.TextField(
        "Technical notes",
        blank=True,
        help_text=(
            "Optional notes under the specification table. For a table, add rows in "
            "Specifications, or write one 'Property: value' / 'Property – value' per line."
        ),
    )
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField("Published", default=True)
    is_featured = models.BooleanField("Featured", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.sku)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"sku": self.sku})

    @property
    def image_list(self):
        images = list(self.images.all())
        images.sort(key=lambda image: (image.sort_order, image.id))
        return images

    @property
    def main_image(self):
        images = self.image_list
        return images[0].file if images else None

    def primary_category(self):
        group_rank = {
            Category.Group.MATERIAL: 0,
            Category.Group.SYSTEM: 1,
            Category.Group.INDUSTRY: 2,
            Category.Group.OTHER: 3,
        }
        categories = list(self.categories.all())
        categories.sort(
            key=lambda item: (group_rank.get(item.group, 9), item.sort_order, item.name)
        )
        return categories[0] if categories else None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    file = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.alt_text or self.file.name


class ProductDocument(models.Model):
    product = models.ForeignKey(Product, related_name="documents", on_delete=models.CASCADE)
    file = models.FileField(upload_to="products/documents/")
    title = models.CharField(max_length=160)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title

    @property
    def file_kind(self):
        name = (self.file.name or "").lower()
        if name.endswith(".pdf"):
            return "PDF"
        if name.endswith((".doc", ".docx")):
            return "DOC"
        if name.endswith((".xls", ".xlsx")):
            return "XLS"
        if "." in name:
            return name.rsplit(".", 1)[-1].upper()
        return "File"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, related_name="specifications", on_delete=models.CASCADE)
    label = models.CharField("Property", max_length=120)
    value = models.CharField(max_length=400)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"

