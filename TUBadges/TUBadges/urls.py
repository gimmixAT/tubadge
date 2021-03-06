from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from BadgePortfolio.ajax import issue_badge

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TUBadges.views.home', name='home'),
    # url(r'^TUBadges/', include('TUBadges.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    url(r'^$', 'BadgePortfolio.views.badges'),
    url(r'^badges/?$', 'BadgePortfolio.views.badges'),
    url(r'^badges/(?P<uid>\d+)/?$', 'BadgePortfolio.views.badges'),
    url(r'^presets/$', 'BadgePortfolio.views.presets'),

    url(r'^svg$', 'BadgePortfolio.svg.build_svg'),
    url(r'^bgsvg$', 'BadgePortfolio.svg.build_bg_svg'),

    url(r'^ajax/issueform$', 'BadgePortfolio.ajax.issue_badge_form'),
    url(r'^ajax/issue$', 'BadgePortfolio.ajax.issue_badge'),
    url(r'^ajax/badge', 'BadgePortfolio.ajax.badge_detail'),
    url(r'^ajax/presetform$', 'BadgePortfolio.ajax.badge_preset_form'),
    url(r'^ajax/preset$', 'BadgePortfolio.ajax.badge_preset_detail'),
    url(r'^ajax/minpreset$', 'BadgePortfolio.ajax.badge_preset'),
    url(r'^ajax/savepreset$', 'BadgePortfolio.ajax.save_badge_preset'),
    url(r'^ajax/duplicatepreset$', 'BadgePortfolio.ajax.duplicate_badge_preset'),
    url(r'^ajax/deletepreset$', 'BadgePortfolio.ajax.delete_badge_preset'),
    url(r'^ajax/togglepublic$', 'BadgePortfolio.ajax.toggle_public'),
    url(r'^ajax/users$', 'BadgePortfolio.ajax.get_users'),
    url(r'^ajax/students', 'BadgePortfolio.ajax.get_users', {'students': True}),
    url(r'^ajax/courses$', 'BadgePortfolio.ajax.get_courses'),
    url(r'^ajax/tag', 'BadgePortfolio.ajax.get_tags'),
    url(r'^ajax/candidates', 'BadgePortfolio.ajax.get_candidate_count')

)
