from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.core.exceptions import ValidationError
import re


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


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

    @staticmethod
    def get_matching_user(query):
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

    @staticmethod
    def get_matching_users(query):
        """
        :type query: String
        """
        parts = query.split(' ', 2)
        if len(parts) is 2:
            return BadgeUser.objects.filter(Q(email__icontains=query) | Q(student_id__startswith=query) | (Q(firstname__icontains=parts[0]) & Q(lastname__icontains=parts[1])))
        else:
            return BadgeUser.objects.filter(Q(email__icontains=query) | Q(student_id__startswith=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query))

    def __unicode__(self):
        return self.firstname+" "+self.lastname+" ("+self.email+")"

    def credibility(self, rating):
        bc = self.issued_badges.filter(rating=rating).count()
        tbc = self.issued_badges.count()
        return 1 - pow((float(bc) / float(tbc)), Badge.factor(rating))


class LVA(models.Model):
    institute = models.PositiveIntegerField(max_length=3)
    number = models.PositiveIntegerField(max_length=3)
    title = models.CharField(max_length=300)
    tutors = models.ManyToManyField(BadgeUser)
    students = models.IntegerField()

    def __unicode__(self):
        return (self.institute and unicode(self.institute)+"." or "") + (self.number and unicode(self.number)+" " or "") + self.title

    class Meta:
        unique_together = ('institute', 'number')


class BadgePreset(models.Model):
    owner = models.ForeignKey(BadgeUser, related_name='badge_presets')
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)


class Badge(models.Model):
    GOLD = 2
    SILVER = 1
    BRONZE = 0
    BADGE_VALUE = (
        (BRONZE, 'Bronze'),
        (SILVER, 'Silber'),
        (GOLD, 'Gold')
    )
    awardee = models.ForeignKey(BadgeUser, related_name='my_badges')
    issuer = models.ForeignKey(BadgeUser, related_name='issued_badges')
    awarder = models.CharField(max_length=200)
    preset = models.ForeignKey(BadgePreset, related_name='issued_badges')
    rating = models.PositiveIntegerField(choices=BADGE_VALUE, default=BRONZE)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)
    proof = models.TextField()
    comment = models.TextField()
    lva = models.ForeignKey(LVA, related_name='awarded_badges', null=True)
    context = models.CharField(max_length=100, blank=True, null=True)
    public = models.BooleanField(default=False)
    candidates = models.IntegerField()

    class Meta:
        unique_together = ('awardee', 'preset')

    @property
    def rating_name(self):
        return Badge.BADGE_VALUE[self.rating][1]

    @property
    def awarder_name(self):
        if self.awarder.isnumeric() and BadgeUser.objects.filter(id=int(self.awarder)).exists():
            a = BadgeUser.objects.get(id=int(self.awarder));
            return a.firstname+' '+a.lastname
        else:
            return self.awarder

    @property
    def via(self):
        if self.issuer_id != int(self.awarder):
            return self.issuer.firstname+' '+self.issuer.lastname
        else:
            return None

    @property
    def rarity(self):
        return 1 - pow(float(self.issued) / float(self.candidates), Badge.factor(self.rating))

    @property
    def rarity_percent(self):
        return str(int(round(self.rarity * 100)))

    @property
    def issued(self):
        c = 1
        if self.preset:
            c = Badge.objects.filter(preset_id=self.preset_id).count()

        return c

    @property
    def value(self):
        o = self.issuer.credibility(self.rating)
        return o

    @property
    def value_percent(self):
        return str(int(round(self.value * 100)))

    @staticmethod
    def factor(rating):
        return [2, 1, 0.5][rating]