from rest_framework import serializers
from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    donation_post_title = serializers.CharField(
        source='donation_post.title',
        read_only=True
    )

    class Meta:
        model = Donation
        fields = [
            'id', 'donor_name', 'donor_email', 'donation_post',
            'donation_post_title', 'amount', 'reference',
            'verified', 'created_at'
        ]
        read_only_fields = ['verified', 'reference', 'created_at']


class DonationInitSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=100)
    donation_post = serializers.IntegerField()
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)


class DonationVerifySerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    donation_post = serializers.IntegerField()