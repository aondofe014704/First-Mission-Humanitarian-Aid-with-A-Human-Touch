from django.contrib import admin
from django.utils.html import format_html
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'donor_name', 'donor_email', 'donation_post_title',
        'amount_display', 'verified_status', 'created_at'
    )
    list_filter = ('verified', 'created_at', 'donation_post')
    search_fields = ('donor_email', 'donor_name', 'reference', 'donation_post__title')
    readonly_fields = ('reference', 'created_at', 'verified')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_email')
        }),
        ('Donation Details', {
            'fields': ('donation_post', 'amount', 'verified', 'reference')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def donation_post_title(self, obj):
        return obj.donation_post.title

    donation_post_title.short_description = 'Campaign'

    def amount_display(self, obj):
        amount = float(obj.amount)
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">₦{:,.2f}</span>',
            amount
        )

    amount_display.short_description = 'Amount'

    def verified_status(self, obj):
        if obj.verified:
            return format_html(
                '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 4px; font-size: 11px;">✓ VERIFIED</span>'
            )
        return format_html(
            '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 4px; font-size: 11px;">✗ PENDING</span>'
        )

    verified_status.short_description = 'Status'