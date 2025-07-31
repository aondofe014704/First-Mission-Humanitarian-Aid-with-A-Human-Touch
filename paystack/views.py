import time
import hmac
import hashlib
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from .models import Donation
from .serializers import DonationSerializer
from post.models import DonationPost
from django.contrib.auth.models import User


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def get_queryset(self):
        # Authenticated users only see their own donations; anonymous cannot list (you can adjust if needed)
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return Donation.objects.none()

    def perform_create(self, serializer):
        raise NotImplementedError("Use the custom init_donation action to start a donation.")

    @action(detail=False, methods=['post'], url_path='init', permission_classes=[AllowAny])
    def init_donation(self, request):
        amount = request.data.get('amount')
        donation_post_id = request.data.get('donation_post')
        donor_email = request.data.get('email')
        donor_name = request.data.get('name', None)

        if not amount or not donation_post_id or not donor_email:
            return Response(
                {"error": "Amount, donation_post, and email are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)
            if amount < 100:
                return Response(
                    {"error": "Amount must be at least ₦100"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            donation_post = DonationPost.objects.get(id=donation_post_id)
        except DonationPost.DoesNotExist:
            return Response(
                {"error": "Invalid donation_post ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = f"DON_{donation_post.id}_{int(amount)}_{int(time.time())}"

        # Initialize Paystack transaction
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SETTINGS['SECRET_KEY']}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": donor_email,
            "amount": int(amount * 100),  # Paystack expects kobo
            "currency": settings.PAYSTACK_SETTINGS.get("CURRENCY", "NGN"),
            "reference": reference,
            "metadata": {
                "donation_post_id": donation_post.id,
                "donation_post_title": donation_post.title,
                "donor_name": donor_name or "",
                "donor_email": donor_email,
                # Optionally include user_id if authenticated
                **({"user_id": request.user.id} if request.user.is_authenticated else {}),
            },
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
        except Exception as e:
            return Response(
                {"error": "Failed to reach Paystack to initialize transaction."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not data.get("status"):
            return Response(
                {"error": data.get("message", "Failed to initialize transaction")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "public_key": settings.PAYSTACK_SETTINGS["PUBLIC_KEY"],
                "email": donor_email,
                "name": donor_name or "",
                "amount": int(amount * 100),
                "donation_post": donation_post.id,
                "donation_post_title": donation_post.title,
                "reference": data["data"]["reference"],
                "authorization_url": data["data"]["authorization_url"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify", permission_classes=[AllowAny])
    def verify_donation(self, request):
        reference = request.data.get("reference")
        amount = request.data.get("amount")
        donation_post_id = request.data.get("donation_post")

        if not reference or not amount or not donation_post_id:
            return Response(
                {"error": "Reference, amount, and donation_post are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = float(amount)
            if amount < 100:
                return Response(
                    {"error": "Amount must be at least ₦100"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid amount format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            donation_post = DonationPost.objects.get(id=donation_post_id)
        except DonationPost.DoesNotExist:
            return Response(
                {"error": "Invalid donation_post ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify transaction with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SETTINGS['SECRET_KEY']}"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
        except Exception:
            return Response(
                {"error": "Failed to reach Paystack for verification."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not data.get("status") or data.get("data", {}).get("status") != "success":
            return Response(
                {"error": data.get("message", "Payment verification failed")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paystack_amount = data.get("data", {}).get("amount", 0)
        if paystack_amount != int(amount * 100):
            return Response(
                {"error": "Amount mismatch"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract metadata to fill donor info
        metadata = data.get("data", {}).get("metadata", {}) or {}
        donor_email = metadata.get("donor_email") or request.data.get("email")
        donor_name = metadata.get("donor_name") or request.data.get("name", None)
        user = None
        user_id = metadata.get("user_id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None
        elif request.user and request.user.is_authenticated:
            user = request.user

        # Save or update donation record
        donation_obj, created = Donation.objects.update_or_create(
            reference=reference,
            defaults={
                "user": user if user and user.is_authenticated else None,
                "donor_email": donor_email,
                "donor_name": donor_name,
                "amount": amount,
                "verified": True,
                "donation_post": donation_post,
            },
        )

        return Response(
            {"message": "Payment verified and saved.", "donation_id": donation_obj.id},
            status=status.HTTP_200_OK,
        )

@api_view(['POST'])
def paystack_webhook(request):
    # Verify webhook signature
    secret_key = settings.PAYSTACK_SETTINGS['SECRET_KEY'].encode('utf-8')
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    payload = request.body

    computed_signature = hmac.new(secret_key, payload, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(computed_signature, signature):
        return Response({"error": "Invalid webhook signature"}, status=status.HTTP_400_BAD_REQUEST)

    event = request.data.get('event')
    data = request.data.get('data')

    if event == 'charge.success':
        reference = data.get('reference')
        amount = data.get('amount') / 100
        metadata = data.get('metadata', {})

        donation_post_id = metadata.get('donation_post_id')
        donor_email = metadata.get('donor_email')
        donor_name = metadata.get('donor_name', 'Anonymous')
        user_id = metadata.get('user_id')  # Optional

        try:
            donation_post = DonationPost.objects.get(id=donation_post_id)
        except DonationPost.DoesNotExist:
            return Response({"error": "Invalid donation post"}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None

        Donation.objects.update_or_create(
            reference=reference,
            defaults={
                "user": user,
                "donor_email": donor_email,
                "donor_name": donor_name,
                "amount": amount,
                "verified": True,
                "donation_post": donation_post
            }
        )
    return Response(status=status.HTTP_200_OK)