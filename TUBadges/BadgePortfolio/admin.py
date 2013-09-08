from django.contrib import admin
from BadgePortfolio.models import BadgeUser, LVA
from BadgePortfolio.forms import BadgeUserForm, LVAForm


class BadgeUserAdmin(admin.ModelAdmin):
    form = BadgeUserForm

admin.site.register(BadgeUser, BadgeUserAdmin)


class LVAAdmin(admin.ModelAdmin):
    form = LVAForm

admin.site.register(LVA, LVAAdmin)