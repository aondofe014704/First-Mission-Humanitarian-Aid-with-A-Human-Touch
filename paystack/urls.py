from django.urls import path
from .views import DonationViewSet, paystack_webhook

urlpatterns = [
    path('', DonationViewSet.as_view({'get': 'list', 'post': 'create'}), name='donation-list'),
    path('init/', DonationViewSet.as_view({'post': 'init_donation'}), name='donation-init'),
    path('verify/', DonationViewSet.as_view({'post': 'verify_donation'}), name='donation-verify'),
    path('webhook/', paystack_webhook, name='paystack_webhook'),
]