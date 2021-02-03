from django.contrib.auth.models import User
from django.db import models

from conf.settings import MEDIA_COMPANY_IMAGE_DIR, MEDIA_SPECIALITY_IMAGE_DIR


class Company(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    logo = models.ImageField(upload_to=MEDIA_COMPANY_IMAGE_DIR, null=True)
    description = models.TextField()
    employee_count = models.IntegerField()
    owner = models.ForeignKey(User, related_name="company", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Company {self.id} : {self.title}'


class Specialty(models.Model):
    code = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    picture = models.ImageField(upload_to=MEDIA_SPECIALITY_IMAGE_DIR, null=True)

    def __str__(self):
        return f'Specialty {self.code} : {self.title}'


class Vacancy(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=64)
    specialty = models.ForeignKey(Specialty, related_name='vacancies', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='vacancies', on_delete=models.CASCADE)
    skills = models.CharField(max_length=1024)
    description = models.TextField()
    salary_from = models.IntegerField()
    salary_to = models.IntegerField()
    posted = models.DateField()

    def __str__(self):
        return f'Vacancy {self.id} : {self.title}'


class Application(models.Model):
    written_username = models.CharField(max_length=128)
    written_phone = models.CharField(max_length=64)
    written_cover_letter = models.TextField()
    vacancy = models.ForeignKey(Vacancy, related_name="applications", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="applications", on_delete=models.CASCADE, blank=True, null=True)
