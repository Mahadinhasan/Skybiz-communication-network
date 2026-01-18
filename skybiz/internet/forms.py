from django import forms
from django.contrib.auth.models import User
from .models import Branch
import os

class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
        'placeholder': 'Password'
    }))

class AdminRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
        'placeholder': 'Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Email'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

# class ImageUploadForm(forms.ModelForm):
#     class Meta:
#         model = CarouselImage
#         fields = ['title', 'caption', 'image', 'is_active']
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
#                 'placeholder': 'Image Title'
#             }),
#             'caption': forms.Textarea(attrs={
#                 'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
#                 'placeholder': 'Image Caption (optional)',
#                 'rows': 3
#             }),
#             'image': forms.FileInput(attrs={
#                 'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
#                 'accept': 'image/jpeg,image/jpg,image/png'
#             }),
#             'is_active': forms.CheckboxInput(attrs={
#                 'class': 'h-4 w-4 text-primary dark:text-secondary'
#             }),
#         }

#     def clean_image(self):
#         image = self.cleaned_data.get('image')
#         if image:
#             extension = os.path.splitext(image.name)[1].lower()
#             allowed_extensions = ['.jpeg', '.jpg', '.png']
#             if extension not in allowed_extensions:
#                 raise forms.ValidationError("Only JPEG, JPG, and PNG files are allowed.")
#         return image

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'city', 'state', 'phone', 'email', 'website_link', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Branch Name'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'State'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Email'
            }),
            'website_link': forms.URLInput(attrs={
                'class': 'w-full p-2 border rounded-lg dark:bg-gray-700 dark:text-gray-200',
                'placeholder': 'Website Link (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary dark:text-secondary'
            }),
        }

    def clean_website_link(self):
        website_link = self.cleaned_data.get('website_link')
        if website_link:
            # Ensure URL starts with http:// or https://
            if not website_link.startswith(('http://', 'https://')):
                website_link = 'https://' + website_link
        return website_link