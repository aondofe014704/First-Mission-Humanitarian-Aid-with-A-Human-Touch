from django import forms
from django.contrib import admin
from .models import Story, DonationPost
import cloudinary.uploader

# Story Admin
class StoryAdminForm(forms.ModelForm):
    image_file = forms.ImageField(required=False, help_text="Upload from local device.")

    class Meta:
        model = Story
        fields = ['title', 'description', 'image_file']

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image_file')
        if image:
            uploaded = cloudinary.uploader.upload(image)
            instance.image_url = uploaded['secure_url']
        if commit:
            instance.save()
        return instance

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    form = StoryAdminForm
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)


# DonationPost Admin
class DonationPostAdminForm(forms.ModelForm):
    image_file = forms.ImageField(required=False, help_text="Upload from local device.")

    class Meta:
        model = DonationPost
        fields = ['title', 'description', 'image_file']

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image_file')
        if image:
            uploaded = cloudinary.uploader.upload(image)
            instance.image_url = uploaded['secure_url']
        if commit:
            instance.save()
        return instance

@admin.register(DonationPost)
class DonationPostAdmin(admin.ModelAdmin):
    form = DonationPostAdminForm
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
