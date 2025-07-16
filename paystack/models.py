from django.conf import settings
from django.db import models
from post.models import DonationPost

class Donation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
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
        return f"{self.user.email} - {self.amount} for {self.donation_post.title}"
