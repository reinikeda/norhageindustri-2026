from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.validators import validate_image_file


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Page(TimeStamped):
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text=(
            "Must match the public page: home, solutions, about, wholesale, contact, "
            "quote, services, cases, terms, privacy, cookies."
        ),
    )
    title = models.CharField(max_length=160)
    heading = models.CharField(max_length=160)
    lead = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Plain text. Line breaks are kept on the website.")
    image = models.ImageField(upload_to="pages/", blank=True, validators=[validate_image_file])
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Service(TimeStamped):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="services/", blank=True, validators=[validate_image_file])
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pages:service_detail", kwargs={"slug": self.slug})


class Project(TimeStamped):
    class WorkType(models.TextChoices):
        ASSEMBLY = "assembly", "Assembly"
        RENOVATION = "renovation", "Renovation"
        REPAIR = "repair", "Repair"
        FACADE = "facade", "Façade"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    country = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=160, blank=True, help_text="City or site, if it can be named.")
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    work_type = models.CharField(max_length=20, choices=WorkType.choices, blank=True)
    dimensions = models.CharField(
        max_length=120,
        blank=True,
        help_text="Size as shown to buyers, for example 25 × 90 m (2,250 m²).",
    )
    industry = models.CharField(max_length=120, blank=True)
    image = models.ImageField(
        "Cover image",
        upload_to="projects/",
        blank=True,
        validators=[validate_image_file],
    )
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-year", "sort_order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pages:project_detail", kwargs={"slug": self.slug})

    @property
    def image_list(self):
        images = list(self.images.all())
        images.sort(key=lambda image: (image.sort_order, image.id))
        return images

    @property
    def cover_image(self):
        if self.image:
            return self.image
        images = self.image_list
        return images[0].file if images else None

    def fact_rows(self):
        rows = []
        if self.work_type:
            rows.append(("Type", self.get_work_type_display()))
        if self.country:
            rows.append(("Country", self.country))
        if self.location:
            rows.append(("Location", self.location))
        if self.year:
            rows.append(("Year", str(self.year)))
        if self.dimensions:
            rows.append(("Size", self.dimensions))
        if self.industry:
            rows.append(("Industry", self.industry))
        return rows


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    file = models.ImageField(upload_to="projects/images/", validators=[validate_image_file])
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.alt_text or self.file.name
