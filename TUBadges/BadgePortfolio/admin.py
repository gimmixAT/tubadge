from django.contrib import admin
from BadgePortfolio.models import BadgeUser
from BadgePortfolio.forms import BadgeUserForm


class BadgeUserAdmin(admin.ModelAdmin):
    form = BadgeUserForm

admin.site.register(BadgeUser, BadgeUserAdmin)