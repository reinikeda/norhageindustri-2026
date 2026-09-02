from django import forms
from django.forms import inlineformset_factory

from products.models import Product

from .models import Inquiry, InquiryLine


CONTACT_WIDGETS = {
    "name": forms.TextInput(attrs={"autocomplete": "name"}),
    "company": forms.TextInput(attrs={"autocomplete": "organization"}),
    "email": forms.EmailInput(attrs={"autocomplete": "email"}),
    "phone": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
}


class HoneypotMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"] = forms.CharField(
            required=False,
            label="Website",
            widget=forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "tabindex": "-1",
                    "aria-hidden": "true",
                }
            ),
        )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Please try again.")
        return cleaned


class ContactForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ("name", "company", "email", "phone", "message")
        labels = {
            "name": "Your name",
            "company": "Company",
            "email": "Work email",
            "phone": "Phone",
            "message": "How can we help?",
        }
        widgets = {
            **CONTACT_WIDGETS,
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True


class QuoteForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ("name", "company", "email", "phone", "country", "message")
        labels = {
            "name": "Your name",
            "company": "Company",
            "email": "Work email",
            "phone": "Phone",
            "country": "Delivery country",
            "message": "Project notes (optional)",
        }
        widgets = {
            **CONTACT_WIDGETS,
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].required = True


class InquiryLineForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        empty_label="Select a product",
    )
    quantity = forms.IntegerField(min_value=1, required=False)

    class Meta:
        model = InquiryLine
        fields = ("product", "quantity")

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        quantity = cleaned.get("quantity")
        if product and not quantity:
            self.add_error("quantity", "Enter a quantity of 1 or more.")
        if quantity and not product:
            self.add_error("product", "Select a product for this quantity.")
        return cleaned

    def save(self, commit=True):
        line = super().save(commit=False)
        if line.product_id:
            line.sku = line.product.sku
            line.product_name = line.product.name
        if commit and line.product_id:
            line.save()
        return line


InquiryLineFormSet = inlineformset_factory(
    Inquiry,
    InquiryLine,
    form=InquiryLineForm,
    extra=3,
    max_num=8,
    can_delete=False,
)
