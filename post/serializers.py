from rest_framework import serializers
from .models import Story, DonationPost

class StorySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Story
        fields = ['id', 'title', 'description', 'image', 'image_url', 'author_name', 'created_at']
        read_only_fields = ['image_url', 'author_name', 'created_at']


class DonationPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = DonationPost
        fields = ['id', 'title', 'description', 'image', 'image_url', 'author_name', 'created_at']
        read_only_fields = ['image_url', 'author_name', 'created_at']
