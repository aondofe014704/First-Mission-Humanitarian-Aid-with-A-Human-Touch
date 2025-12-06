from django.db import models
from django.core.validators import MinValueValidator
from post.models import DonationPost


class Donation(models.Model):
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField(db_index=True)
    donation_post = models.ForeignKey(
        DonationPost,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(100)]
    )
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'verified']),
            models.Index(fields=['donation_post', 'verified']),
        ]

    def __str__(self):
        return f"{self.donor_name} - ₦{self.amount} for {self.donation_post.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Update donation post total if verified
        if self.verified and (is_new or 'verified' in kwargs.get('update_fields', [])):
            self.donation_post.update_total_donated()