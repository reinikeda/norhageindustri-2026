from django.contrib import admin

from .models import Inquiry, InquiryLine


class InquiryLineInline(admin.TabularInline):
    model = InquiryLine
    extra = 0
    readonly_fields = ("sku", "product_name")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("created_at", "kind", "company", "email", "status")
    list_filter = ("kind", "status", "created_at")
    search_fields = ("name", "company", "email", "phone", "message")
    readonly_fields = ("created_at", "updated_at", "ip_address", "source_path")
    inlines = [InquiryLineInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "kind",
                    "status",
                    "name",
                    "company",
                    "email",
                    "phone",
                    "country",
                    "message",
                )
            },
        ),
        (
            "Internal",
            {
                "fields": (
                    "internal_notes",
                    "source_path",
                    "ip_address",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
