from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()


@receiver(post_migrate)
def create_superuser_on_deploy(sender, **kwargs):
    """
    Auto-create superuser on production deployment.
    Only runs once when no superuser exists.
    """
    # Only run for django.contrib.auth app to avoid multiple executions
    if sender.name != 'django.contrib.auth':
        return

    # Only run in production
    if settings.DEBUG:
        return

    # Check if superuser exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser exists, skipping creation")
    else:
        # Get credentials from environment
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if email and password:
            try:
                User.objects.create_superuser(email=email, password=password)
                print(f"✅ Superuser created: {email}")
            except Exception as e:
                print(f"❌ Failed to create superuser: {e}")
        else:
            print("⚠️  Set DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD")