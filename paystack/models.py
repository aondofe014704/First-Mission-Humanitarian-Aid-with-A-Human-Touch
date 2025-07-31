from django.conf import settings
from django.db import models
from post.models import DonationPost

class Donation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations',
    )
    donor_name = models.CharField(max_length=100, blank=True, null=True)
    donor_email = models.EmailField(blank=True, null=True)

    donation_post = models.ForeignKey(
        DonationPost,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name_or_email = self.donor_name or self.donor_email or (self.user.email if self.user else "Anonymous")
        return f"{name_or_email} - ₦{self.amount} for {self.donation_post.title}"
