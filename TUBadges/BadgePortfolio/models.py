from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.core.exceptions import ValidationError


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class LVA(models.Model):
    institute = models.PositiveIntegerField(max_length=3)
    number = models.PositiveIntegerField(max_length=3)
    title = models.CharField(max_length=300)
    tutors = models.ManyToManyField(User)

    class Meta:
        unique_together = ('institute', 'number')


class BadgeUser(models.Model):
    STUDENT = 'stud'
    PROFESSOR = 'prof'
    ROLES = (
        (STUDENT, 'Student'),
        (PROFESSOR, 'Professor')
    )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    student_id = models.CharField(max_length=10)
    object_id = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=4, choices=ROLES, default=STUDENT)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __unicode__(self):
        return self.firstname+" "+self.lastname+" ("+self.email+")"


class BadgePreset(models.Model):
    owner = models.ForeignKey(User, related_name='badge_presets')
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)

    class Meta:
        permissions = (
            ("can_have_presets", "Can create, view, edit and delete his own BadgePresets"),
        )


class Badge(models.Model):
    GOLD = 2
    SILVER = 1
    BRONZE = 0
    BADGE_VALUE = (
        (GOLD, 'Gold'),
        (SILVER, 'Silber'),
        (BRONZE, 'Bronze')
    )
    awardee = models.EmailField()
    issuer = models.ForeignKey(User, related_name='issued_badges')
    awarder = models.CharField(max_length=200)
    preset = models.ForeignKey(BadgePreset)
    rating = models.PositiveIntegerField(choices=BADGE_VALUE, default=BRONZE)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)
    proof_url = models.URLField()
    lva = models.ForeignKey(LVA, related_name='awarded_badges')
    public = models.BooleanField(default=False)