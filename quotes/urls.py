from django.urls import path

from .views import InquiryThanksView, QuotePageView

app_name = "quotes"

urlpatterns = [
    path("sent/", InquiryThanksView.as_view(), name="thanks"),
    path("", QuotePageView.as_view(), name="request"),
]
