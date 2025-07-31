from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'donation_post', 'amount', 'verified', 'reference', 'created_at')
    search_fields = ('donor_email', 'donation_post__title', 'reference')
    list_filter = ('verified', 'created_at')

