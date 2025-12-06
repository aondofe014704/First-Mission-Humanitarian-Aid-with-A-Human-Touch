from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Story, DonationPost
import cloudinary.uploader


class BasePostAdminForm(forms.ModelForm):
    """Base form for uploading images"""
    image_file = forms.ImageField(
        required=False,
        help_text="Upload image (max 5MB). Recommended size: 1200x800px",
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control'
        })
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image_file')
        if image:
            uploaded = cloudinary.uploader.upload(
                image,
                folder=f"{self.Meta.model.__name__.lower()}s",
                transformation=[
                    {'width': 1200, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            instance.image_url = uploaded['secure_url']
        if commit:
            instance.save()
        return instance


class StoryAdminForm(BasePostAdminForm):
    class Meta:
        model = Story
        fields = ['title', 'description', 'image_file']


class DonationPostAdminForm(BasePostAdminForm):
    class Meta:
        model = DonationPost
        fields = ['title', 'description', 'image_file']


class BasePostAdmin(admin.ModelAdmin):
    """Base admin with common configuration"""
    list_display = ('title', 'author_name', 'image_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'image_display', 'author')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Media', {
            'fields': ('image_file', 'image_display', 'image_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('author', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def author_name(self, obj):
        return obj.author.email if obj.author else 'No Author'

    author_name.short_description = 'Author'

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return format_html('<span style="color: #999;">No image</span>')

    image_preview.short_description = 'Image'

    def image_display(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image_url
            )
        return format_html('<p style="color: #999;">No image uploaded yet</p>')

    image_display.short_description = 'Current Image'

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',)
        }


@admin.register(Story)
class StoryAdmin(BasePostAdmin):
    form = StoryAdminForm


@admin.register(DonationPost)
class DonationPostAdmin(BasePostAdmin):
    form = DonationPostAdminForm
    list_display = BasePostAdmin.list_display + ('total_donated_display',)

    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Media', {
            'fields': ('image_file', 'image_display', 'image_url'),
            'classes': ('collapse',)
        }),
        ('Donation Stats', {
            'fields': ('total_donated',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('author', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def total_donated_display(self, obj):
        amount = float(obj.total_donated)
        color = '#28a745' if amount > 0 else '#999'
        return format_html(
            '<span style="color: {}; font-weight: bold;">₦{:,.2f}</span>',
            color, amount
        )

    total_donated_display.short_description = 'Total Donated'