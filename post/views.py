from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.core.cache import cache
from .models import Story, DonationPost
from .serializers import StorySerializer, DonationPostSerializer
import cloudinary.uploader

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().order_by('-created_at')
    serializer_class = StorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        cached = cache.get('stories')
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('stories', response.data, timeout=3600)
        return response

    def perform_create(self, serializer):
        image_file = self.request.data.get('image')
        image_url = None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        serializer.save(author=self.request.user, image_url=image_url)
        cache.delete('stories')

    def perform_update(self, serializer):
        image_file = self.request.data.get('image')
        image_url = serializer.instance.image_url
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        serializer.save(image_url=image_url)
        cache.delete('stories')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('stories')


class DonationPostViewSet(viewsets.ModelViewSet):
    queryset = DonationPost.objects.all().order_by('-created_at')
    serializer_class = DonationPostSerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        cached = cache.get('donations')
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set('donations', response.data, timeout=3600)
        return response

    def perform_create(self, serializer):
        image_file = self.request.data.get('image')
        image_url = None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        serializer.save(author=self.request.user, image_url=image_url)
        cache.delete('donations')

    def perform_update(self, serializer):
        image_file = self.request.data.get('image')
        image_url = serializer.instance.image_url
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('secure_url')
        serializer.save(image_url=image_url)
        cache.delete('donations')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('donations')
