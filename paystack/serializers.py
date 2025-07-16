from rest_framework import serializers
from .models import Donation
from post.models import DonationPost

class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.ReadOnlyField(source='user.name')
    donor_email = serializers.ReadOnlyField(source='user.email')
    donation_post_title = serializers.ReadOnlyField(source='donation_post.title')

    class Meta:
        model = Donation
        fields = [
            'id', 'user', 'donor_name', 'donor_email',
            'donation_post', 'donation_post_title',
            'amount', 'reference', 'verified', 'created_at'
        ]
        read_only_fields = [
            'user', 'donor_name', 'donor_email',
            'verified', 'reference', 'created_at',
            'donation_post_title'
        ]
