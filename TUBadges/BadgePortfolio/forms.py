from django import forms
from django.contrib import admin
from BadgePortfolio.models import BadgeUser, LVA


class BadgeUserForm(forms.ModelForm):

    class Meta:
        model = BadgeUser

    def save(self, commit=True):
        user = super(BadgeUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LVAForm(forms.ModelForm):

    class Meta:
        model = LVA