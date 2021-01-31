import json
import os

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
django.setup()

from job_search.models import Vacancy, Company, Specialty

if __name__ == '__main__':
    with open('../mock_data.json') as file:
        mock_data = json.load(file)

    for company in mock_data['companies']:
        Company.objects.create(**company)

    for specialty in mock_data['specialties']:
        Specialty.objects.create(**specialty)

    for job in mock_data['jobs']:
        job['specialty'] = Specialty.objects.get(code=job['specialty'])
        job['company'] = Company.objects.get(id=job['company'])
        Vacancy.objects.create(**job)
