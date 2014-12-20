from django.contrib import admin
from BadgePortfolio.models import *
from BadgePortfolio.forms import BadgeUserForm, LVAForm

class BadgeReferenceInline(admin.TabularInline):
    model = Badge
    fk_name = 'awardee'

class BadgeUserAdmin(admin.ModelAdmin):
    form = BadgeUserForm
    inlines = [BadgeReferenceInline, ]

admin.site.register(BadgeUser, BadgeUserAdmin)


class LVAAdmin(admin.ModelAdmin):
    form = LVAForm

admin.site.register(LVA, LVAAdmin)