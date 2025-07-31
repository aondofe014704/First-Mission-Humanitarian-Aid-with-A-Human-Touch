from rest_framework import serializers
from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    donation_post_title = serializers.ReadOnlyField(source='donation_post.title')

    class Meta:
        model = Donation
        fields = [
            'id', 'user', 'donor_name', 'donor_email', 'donation_post', 'donation_post_title',
            'amount', 'reference', 'verified', 'created_at'
        ]
        read_only_fields = [
            'user', 'verified', 'reference', 'created_at', 'donation_post_title'
        ]
