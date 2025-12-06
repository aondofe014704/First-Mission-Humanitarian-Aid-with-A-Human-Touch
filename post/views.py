from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Story, DonationPost
from .serializers import StorySerializer, DonationPostSerializer
import cloudinary.uploader


class IsAdminUser(permissions.BasePermission):
    """Only admin/superadmin can create, update, delete"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class BasePostViewSet(viewsets.ModelViewSet):
    """Base viewset with common functionality"""
    permission_classes = [IsAdminUser]
    cache_timeout = 3600

    def get_cache_key(self):
        return f"{self.basename}_list"

    @method_decorator(cache_page(3600))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def _handle_image_upload(self, image_file):
        """Upload image to Cloudinary and return URL"""
        if not image_file:
            return None
        result = cloudinary.uploader.upload(
            image_file,
            folder=f"{self.basename}s",
            transformation=[
                {'width': 1200, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:good'}
            ]
        )
        return result.get('secure_url')

    def perform_create(self, serializer):
        image_file = self.request.data.get('image')
        image_url = self._handle_image_upload(image_file)
        serializer.save(author=self.request.user, image_url=image_url or '')
        cache.delete(self.get_cache_key())

    def perform_update(self, serializer):
        image_file = self.request.data.get('image')
        if image_file:
            image_url = self._handle_image_upload(image_file)
            serializer.save(image_url=image_url)
        else:
            serializer.save()
        cache.delete(self.get_cache_key())

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(self.get_cache_key())


class StoryViewSet(BasePostViewSet):
    queryset = Story.objects.select_related('author').all()
    serializer_class = StorySerializer
    basename = 'story'


class DonationPostViewSet(BasePostViewSet):
    queryset = DonationPost.objects.select_related('author').all()
    serializer_class = DonationPostSerializer
    basename = 'donation'