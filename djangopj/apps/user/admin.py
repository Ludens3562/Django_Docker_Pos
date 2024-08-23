from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from apps.user.models import CustomUser
from django.core.exceptions import PermissionDenied


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["staffcode", "password", "name", "is_staff", "is_superuser", "is_active"]

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if (password or password_confirm) and password != password_confirm:
            raise ValidationError("Passwords don't match")
        return password_confirm


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ["staffcode", "name"]


class UserChangeFormOnlySuperuser(UserCreationForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label="Password confirmation", widget=forms.PasswordInput, required=False)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["staffcode", "name", "last_login", "is_staff", "is_superuser", "is_active", "id"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["staffcode", "name"]
    ordering = ["created_at"]
    filter_horizontal = []

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser and obj.password:
            obj.set_password(obj.password)
        else:
            obj.password = form.initial.get("password")
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs["form"] = UserChangeFormOnlySuperuser
        else:
            kwargs["form"] = UserChangeForm
        return super().get_form(request, obj, **kwargs)

    def add_view(self, request, form_url="", extra_context=None):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().add_view(request, form_url, extra_context)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (None, {"fields": ["staffcode", "password", "password_confirm"]}),
                ("Personal info", {"fields": ["name"]}),
                ("Permissions", {"fields": ["is_staff", "is_superuser", "is_active", "groups"]}),
            )
        else:
            return (
                (None, {"fields": ["staffcode", "password"]}),
                ("Personal info", {"fields": ["name"]}),
            )


# Now register the new UserAdmin...
admin.site.register(CustomUser, UserAdmin)
