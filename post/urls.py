from rest_framework.routers import DefaultRouter
from .views import StoryViewSet, DonationPostViewSet

router = DefaultRouter()
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'donations', DonationPostViewSet, basename='donationpost')

urlpatterns = router.urls
