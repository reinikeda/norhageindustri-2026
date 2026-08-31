from django.conf import settings
from django.core.mail import EmailMessage


def notify_inquiry(inquiry):
    sales = getattr(settings, "SALES_NOTIFY_EMAIL", "") or "info@norhageindustri.com"
    sender = settings.DEFAULT_FROM_EMAIL
    kind = inquiry.get_kind_display()
    lines = "\n".join(
        f"- {line.product_name} (SKU {line.sku}) × {line.quantity}"
        for line in inquiry.lines.all()
    )
    body = (
        f"{kind} request from {inquiry.name} at {inquiry.company}\n"
        f"Email: {inquiry.email}\n"
        f"Phone: {inquiry.phone}\n"
        f"Destination: {inquiry.country or '—'}\n\n"
        f"{inquiry.message or '(no message)'}\n"
    )
    if lines:
        body += f"\nProducts:\n{lines}\n"

    sales_mail = EmailMessage(
        subject=f"{kind}: {inquiry.company}",
        body=body,
        from_email=sender,
        to=[sales],
        reply_to=[inquiry.email],
    )
    sales_mail.send(fail_silently=False)

    confirm = EmailMessage(
        subject="We received your request — Norhage Industri",
        body=(
            f"Hello {inquiry.name},\n\n"
            "Thank you. Sales has your request and will reply from "
            f"{sales}. Prices are quoted per project.\n\n"
            "Norhage Industri / TEHI AS\n"
        ),
        from_email=sender,
        to=[inquiry.email],
        reply_to=[sales],
    )
    confirm.send(fail_silently=False)
