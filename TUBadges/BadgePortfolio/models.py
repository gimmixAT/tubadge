from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.core.exceptions import ValidationError
import re
from datetime import date
from django.db.models.fields import TextField
import uuid


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BadgeUser(models.Model):
    STUDENT = 'stud'
    PROFESSOR = 'prof'
    ROLES = (
        (STUDENT, 'Student'),
        (PROFESSOR, 'Professor')
    )
    email = models.EmailField(unique=True, default=str(uuid.uuid4()) + "@tubadges.iguw.tuwien.ac.at")
    password = models.CharField(max_length=128, blank=True)
    firstname = models.CharField(max_length=50, default="")
    lastname = models.CharField(max_length=50, default="")
    student_id = models.CharField(max_length=10, default=0)
    object_id = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=4, choices=ROLES, default=STUDENT)
    logout_date = models.DateTimeField(null=True, blank=True)

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
        parts2 = query.split(',', 2)
        if len(parts) is 2:
            return BadgeUser.objects.filter(Q(email__icontains=query) | Q(student_id__startswith=query) | (Q(firstname__icontains=parts[0]) & Q(lastname__icontains=parts[1])))
        elif len(parts2) is 2:
            return BadgeUser.objects.filter(Q(student_id__startswith=parts2[0]))
        else:
            return BadgeUser.objects.filter(Q(email__icontains=query) | Q(student_id__startswith=query) | Q(firstname__icontains=query) | Q(lastname__icontains=query))

    def __str__(self):
        return self.student_id + " - " + self.firstname+" "+self.lastname+" ("+self.email+")"

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

    def __str__(self):
        return (self.institute and str(self.institute)+"." or "") + (self.number and str(self.number)+" " or "") + self.title

    class Meta:
        unique_together = ('institute', 'number')


class BadgePreset(models.Model):
    owner = models.ForeignKey(BadgeUser, related_name='badge_presets')
    original = models.ForeignKey('self', related_name='forks', blank=True, null=True)
    name = models.CharField(max_length=200)
    img = models.CharField(max_length=200)
    keywords = models.ManyToManyField(Tag)
    proof = models.TextField(default='', blank=True)
    comment = models.TextField(default='', blank=True)


class Badge(models.Model):
    GOLD = 2
    SILVER = 1
    BRONZE = 0
    BADGE_VALUE = (
        (BRONZE, 'Bronze'),
        (SILVER, 'Silber'),
        (GOLD, 'Gold')
    )
    SUMMER_SEMESTER = 's'
    WINTER_SEMESTER = 'w'
    SEMESTER_VALUE = {
        (SUMMER_SEMESTER, 'Sommersemester'),
        (WINTER_SEMESTER, 'Wintersemester')
    }
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
    date = models.DateField(default=date.today)
    semester = models.CharField(choices=SEMESTER_VALUE, max_length=1)
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('awardee', 'preset')

    @property
    def candidate_count(self):
        return BadgePresetSemesterCounts.objects.get(year=self.year, semester=self.semester, preset_id=self.preset_id).candidates

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
        if not self.awarder.isnumeric() or self.issuer_id != int(self.awarder):
            return self.issuer.firstname+' '+self.issuer.lastname
        else:
            return None

    @property
    def rarity(self):
        return 1 - pow(float(self.issued) / float(self.candidate_count), Badge.factor(self.rating))

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


class BadgePresetSemesterCounts(models.Model):
    preset = models.ForeignKey(BadgePreset, related_name='semester_candidates')
    semester = models.CharField(choices=Badge.SEMESTER_VALUE, max_length=1)
    year = models.PositiveIntegerField()
    candidates = models.PositiveIntegerField()

    class Meta:
        unique_together = ('preset', 'semester', 'year')

    @staticmethod
    def count(year, semester, preset_id):
        c = 1
        if BadgePresetSemesterCounts.objects.filter(year=year, semester=semester, preset_id=preset_id).exists():
            c = BadgePresetSemesterCounts.objects.get(year=year, semester=semester, preset_id=preset_id).candidates
        return c