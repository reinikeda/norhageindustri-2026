import logging

from django.core.cache import cache
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from pages.views import published_page
from products.models import Product

from .emails import notify_inquiry
from .forms import ContactForm, InquiryLineFormSet, QuoteForm
from .models import Inquiry

logger = logging.getLogger(__name__)


def client_ip(request):
    return request.META.get("REMOTE_ADDR")


def rate_key(request):
    return f"inquiry-rate:{client_ip(request) or 'unknown'}"


def too_many_inquiries(request):
    return cache.get(rate_key(request), 0) >= 6


def record_inquiry(request):
    key = rate_key(request)
    cache.set(key, cache.get(key, 0) + 1, 60 * 60)


class InquiryThanksView(TemplateView):
    template_name = "quotes/thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kind = self.request.GET.get("kind", "contact")
        context["kind"] = kind
        context["title"] = "Request received"
        context["meta_description"] = "Norhage Industri has received your request."
        context["robots"] = "noindex, follow"
        return context


class ContactPageView(TemplateView):
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("contact")
        context["page"] = page
        if page:
            context.update(
                {
                    "title": page.seo_title or page.title,
                    "meta_description": page.seo_description or page.lead[:160],
                    "heading": page.heading,
                    "lead": page.lead,
                    "body": page.body,
                }
            )
        else:
            context.update(
                {
                    "title": "Contact",
                    "meta_description": "Contact Norhage Industri for technical advice or a project quote.",
                    "heading": "Contact",
                    "lead": "Use these details for technical questions or a project discussion.",
                    "body": "",
                }
            )
        context.setdefault("form", ContactForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if too_many_inquiries(request):
            form.add_error(None, "Please wait before sending another request.")
        elif form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.kind = Inquiry.Kind.CONTACT
            inquiry.source_path = request.path
            inquiry.ip_address = client_ip(request)
            inquiry.save()
            record_inquiry(request)
            try:
                notify_inquiry(inquiry)
            except Exception:
                logger.exception("Failed to send contact inquiry email")
            return redirect(f"{reverse('quotes:thanks')}?kind=contact")
        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)


class QuotePageView(TemplateView):
    template_name = "quotes/quote.html"

    def selected_product(self):
        sku = self.request.GET.get("sku") or self.request.POST.get("prefill_sku") or ""
        sku = sku.strip()
        if not sku:
            return None
        return Product.objects.filter(sku=sku, is_active=True).first()

    def get_formset(self, data=None):
        product = self.selected_product() if data is None else None
        kwargs = {"instance": Inquiry()}
        if data is not None:
            kwargs["data"] = data
        elif product:
            kwargs["initial"] = [{"product": product.pk, "quantity": 1}]
        return InquiryLineFormSet(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = published_page("quote")
        product = self.selected_product()
        context["page"] = page
        context["title"] = page.seo_title if page and page.seo_title else "Request a quote"
        context["meta_description"] = (
            page.seo_description
            if page and page.seo_description
            else "Ask Norhage Industri for a B2B quote. Include products, quantities, and destination."
        )
        context["heading"] = page.heading if page else "Request a quote"
        context["lead"] = (
            page.lead
            if page
            else (
                "Tell us the products, quantities, and destination. Sales replies with a "
                "project quote — prices are not published on the website."
            )
        )
        context["body"] = page.body if page else ""
        context["selected_product"] = product
        context.setdefault("form", QuoteForm())
        context.setdefault("formset", self.get_formset())
        return context

    def post(self, request, *args, **kwargs):
        form = QuoteForm(request.POST)
        formset = self.get_formset(data=request.POST)
        if too_many_inquiries(request):
            form.add_error(None, "Please wait before sending another request.")
        elif form.is_valid() and formset.is_valid():
            filled = [
                line
                for line in formset.cleaned_data
                if line and not line.get("DELETE") and line.get("product") and line.get("quantity")
            ]
            if not filled:
                form.add_error(None, "Add at least one product and quantity.")
            else:
                with transaction.atomic():
                    inquiry = form.save(commit=False)
                    inquiry.kind = Inquiry.Kind.QUOTE
                    inquiry.source_path = request.get_full_path()
                    inquiry.ip_address = client_ip(request)
                    inquiry.save()
                    for line in filled:
                        product = line["product"]
                        inquiry.lines.create(
                            product=product,
                            sku=product.sku,
                            product_name=product.name,
                            quantity=line["quantity"],
                        )
                record_inquiry(request)
                try:
                    notify_inquiry(inquiry)
                except Exception:
                    logger.exception("Failed to send quote inquiry email")
                return redirect(f"{reverse('quotes:thanks')}?kind=quote")
        context = self.get_context_data()
        context["form"] = form
        context["formset"] = formset
        return render(request, self.template_name, context)
