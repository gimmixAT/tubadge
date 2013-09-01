from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.core.exceptions import ValidationError
import re


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
    student_id = models.CharField(max_length=10, default=0)
    object_id = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=4, choices=ROLES, default=STUDENT)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def get_matching_user(self, query):
        """
        :type query: String
        """
        #check if the query may be an email address
        if query.find('@') >= 0:
            if BadgeUser.objects.exists(email__iexact=query):
                return BadgeUser.objects.get(email__iexact=query)

        #check if the query may be a studentID
        if re.match('^[0-9]{7}$', query, re.IGNORECASE):
            if BadgeUser.objects.exists(studentID=query):
                return BadgeUser.objects.get(studentID=query)

        parts = query.split(' ', 2)
        if len(parts) is 2:
            if BadgeUser.objects.exists(firstname__iexact=parts[0], lastname__iexact=parts[1]):
                return BadgeUser.objects.get(firstname__iexact=parts[0], lastname__iexact=parts[1])

        return None

    def get_matching_users(self, query):
        """
        :type query: String
        """
        parts = query.split(' ', 2)
        if len(parts) is 2:
            return BadgeUser.objects.get(Q(email__icontains=query) | Q(studentID__contains=query) | (Q(firstname__icontains=parts[0]) & Q(lastname__icontains=parts[1])))
        else:
            return BadgeUser.objects.get(Q(email__icontains=query) | Q(studentID__contains=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query) )

    def __unicode__(self):
        return self.firstname+" "+self.lastname+" ("+self.email+")"

    def credibility(self, rating):
        bc = self.issued_badges.filter(rating=rating).count()
        tbc = self.issued_badges.count()
        return 1 - pow((float(bc) / float(tbc)), Badge.factor[self.value])



class BadgePreset(models.Model):
    owner = models.ForeignKey(BadgeUser, related_name='badge_presets')
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
    awardee = models.ForeignKey(BadgeUser, related_name='my_badges')
    issuer = models.ForeignKey(BadgeUser, related_name='issued_badges')
    awarder = models.CharField(max_length=200)
    preset = models.ForeignKey(BadgePreset, related_name='issued_badges')
    rating = models.PositiveIntegerField(choices=BADGE_VALUE, default=BRONZE)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)
    proof_url = models.URLField()
    lva = models.ForeignKey(LVA, related_name='awarded_badges')
    public = models.BooleanField(default=False)
    candidates = models.IntegerField()

    def rarity(self):
        c = 1
        if self.preset is not None:
            c = self.preset.issued_badges.count()

        return 1 - pow(float(c) / float(self.candidates), Badge.factor[self.rating]);

    def value(self):
        self.issuer.credibility(self.rating)

    def factor(self, rating):
        return [2, 1, 0.5][rating]