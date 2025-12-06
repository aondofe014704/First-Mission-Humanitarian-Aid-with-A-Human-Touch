import time
import hmac
import hashlib
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
from .models import Donation
from .serializers import (
    DonationSerializer,
    DonationInitSerializer,
    DonationVerifySerializer
)
from post.models import DonationPost


class DonationViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only access to donations"""
    queryset = Donation.objects.select_related('donation_post').filter(verified=True)
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        post_id = self.request.query_params.get('donation_post')
        if post_id:
            qs = qs.filter(donation_post_id=post_id)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def init(self, request):
        serializer = DonationInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            donation_post = DonationPost.objects.get(id=data['donation_post'])
        except DonationPost.DoesNotExist:
            return Response(
                {"error": "Invalid donation post"},
                status=status.HTTP_404_NOT_FOUND
            )

        reference = f"DON_{donation_post.id}_{int(data['amount'])}_{int(time.time())}"

        # Initialize Paystack transaction
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SETTINGS['SECRET_KEY']}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": data['email'],
            "amount": int(data['amount'] * 100),
            "currency": "NGN",
            "reference": reference,
            "metadata": {
                "donation_post_id": donation_post.id,
                "donation_post_title": donation_post.title,
                "donor_name": data['name'],
                "donor_email": data['email'],
            },
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException:
            return Response(
                {"error": "Payment gateway unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if not result.get("status"):
            return Response(
                {"error": result.get("message", "Failed to initialize")},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "reference": result["data"]["reference"],
            "authorization_url": result["data"]["authorization_url"],
            "amount": int(data['amount'] * 100),
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify(self, request):
        serializer = DonationVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Verify with Paystack
        url = f"https://api.paystack.co/transaction/verify/{data['reference']}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SETTINGS['SECRET_KEY']}"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException:
            return Response(
                {"error": "Verification failed"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if not result.get("status") or result["data"]["status"] != "success":
            return Response(
                {"error": "Payment not successful"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate amount
        if result["data"]["amount"] != int(data['amount'] * 100):
            return Response(
                {"error": "Amount mismatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        metadata = result["data"].get("metadata", {})

        try:
            donation_post = DonationPost.objects.get(id=data['donation_post'])
        except DonationPost.DoesNotExist:
            return Response(
                {"error": "Invalid donation post"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save donation
        with transaction.atomic():
            donation, created = Donation.objects.update_or_create(
                reference=data['reference'],
                defaults={
                    "donor_email": metadata.get("donor_email"),
                    "donor_name": metadata.get("donor_name", "Anonymous"),
                    "amount": data['amount'],
                    "verified": True,
                    "donation_post": donation_post,
                }
            )

        return Response({
            "message": "Donation verified successfully",
            "donation_id": donation.id
        })


@api_view(['POST'])
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    secret_key = settings.PAYSTACK_SETTINGS['SECRET_KEY'].encode('utf-8')
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')

    computed_signature = hmac.new(
        secret_key,
        request.body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        return Response(
            {"error": "Invalid signature"},
            status=status.HTTP_400_BAD_REQUEST
        )

    event = request.data.get('event')
    data = request.data.get('data', {})

    if event == 'charge.success':
        reference = data.get('reference')
        amount = data.get('amount', 0) / 100
        metadata = data.get('metadata', {})

        try:
            donation_post = DonationPost.objects.get(
                id=metadata.get('donation_post_id')
            )
        except DonationPost.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        with transaction.atomic():
            Donation.objects.update_or_create(
                reference=reference,
                defaults={
                    "donor_email": metadata.get('donor_email'),
                    "donor_name": metadata.get('donor_name', 'Anonymous'),
                    "amount": amount,
                    "verified": True,
                    "donation_post": donation_post
                }
            )

    return Response(status=status.HTTP_200_OK)