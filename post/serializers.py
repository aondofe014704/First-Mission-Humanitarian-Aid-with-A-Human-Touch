from rest_framework import serializers
from .models import Story, DonationPost


class BasePostSerializer(serializers.ModelSerializer):
    """Base serializer with common fields"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        abstract = True
        read_only_fields = ['image_url', 'author_name', 'created_at']


class StorySerializer(BasePostSerializer):
    class Meta:
        model = Story
        fields = ['id', 'title', 'description', 'image', 'image_url',
                  'author_name', 'created_at']
        read_only_fields = BasePostSerializer.Meta.read_only_fields


class DonationPostSerializer(BasePostSerializer):
    total_donated = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = DonationPost
        fields = ['id', 'title', 'description', 'image', 'image_url',
                  'author_name', 'total_donated', 'created_at']
        read_only_fields = BasePostSerializer.Meta.read_only_fields + ['total_donated']