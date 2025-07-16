from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from .models import Donation
from .serializers import DonationSerializer
from post.models import DonationPost
import requests

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see their own donations
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        raise NotImplementedError("Use the custom init_donation action to start a donation.")

    @action(detail=False, methods=['post'], url_path='init')
    def init_donation(self, request):
        amount = request.data.get('amount')
        donation_post_id = request.data.get('donation_post')

        if not amount or not donation_post_id:
            return Response({"error": "Amount and donation_post are required"}, status=400)

        try:
            donation_post = DonationPost.objects.get(id=donation_post_id)
        except DonationPost.DoesNotExist:
            return Response({"error": "Invalid donation_post ID"}, status=400)

        user = request.user
        return Response({
            "public_key": settings.PAYSTACK_SETTINGS['PUBLIC_KEY'],
            "email": user.email,
            "name": user.name,
            "amount": int(amount) * 100,
            "donation_post": donation_post.id,
            "donation_post_title": donation_post.title
        })

    @action(detail=False, methods=['post'], url_path='verify')
    def verify_donation(self, request):
        reference = request.data.get('reference')
        amount = request.data.get('amount')
        donation_post_id = request.data.get('donation_post')

        if not reference or not amount or not donation_post_id:
            return Response({"error": "Reference, amount, and donation_post are required"}, status=400)

        # Verify with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SETTINGS['SECRET_KEY']}"
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data.get('status'):
            return Response({"error": "Payment verification failed"}, status=400)

        try:
            donation_post = DonationPost.objects.get(id=donation_post_id)
        except DonationPost.DoesNotExist:
            return Response({"error": "Invalid donation_post ID"}, status=400)

        # Save or update the donation
        Donation.objects.update_or_create(
            reference=reference,
            defaults={
                "user": request.user,
                "amount": amount,
                "verified": True,
                "donation_post": donation_post
            }
        )

        return Response({"message": "Payment verified and saved."}, status=200)
