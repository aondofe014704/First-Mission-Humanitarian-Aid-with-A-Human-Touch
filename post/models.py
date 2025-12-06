from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField

User = get_user_model()


class BasePost(models.Model):
    """Abstract base model for common fields"""
    title = models.CharField(max_length=250, db_index=True)
    description = RichTextField(
        config_name='default',
        help_text="Use the editor to format your content with bold, italic, lists, etc."
    )
    image_url = models.URLField(blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_posts"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Story(BasePost):
    class Meta(BasePost.Meta):
        verbose_name_plural = 'Stories'


class DonationPost(BasePost):
    total_donated = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        db_index=True
    )

    class Meta(BasePost.Meta):
        verbose_name_plural = 'Donation Posts'

    def update_total_donated(self):
        """Update total from verified donations"""
        from django.db.models import Sum
        total = self.donations.filter(verified=True).aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        self.total_donated = total
        self.save(update_fields=['total_donated'])