from django.db import models
from django.urls import reverse


class Inquiry(models.Model):
    class Kind(models.TextChoices):
        CONTACT = "contact", "Contact"
        QUOTE = "quote", "Quote"

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        CLOSED = "closed", "Closed"

    kind = models.CharField(max_length=20, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    name = models.CharField(max_length=160)
    company = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=60)
    country = models.CharField("Destination country", max_length=120, blank=True)
    message = models.TextField(blank=True)
    source_path = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.get_kind_display()} from {self.company} ({self.email})"

    def get_absolute_url(self):
        return reverse("admin:quotes_inquiry_change", args=[self.pk])


class InquiryLine(models.Model):
    inquiry = models.ForeignKey(Inquiry, related_name="lines", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inquiry_lines",
    )
    sku = models.CharField(max_length=64)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.sku} × {self.quantity}"
