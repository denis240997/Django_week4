from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from job_search.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='main'),

    path('vacancies/', ListVacancyViewAll.as_view(), name='vacancies_all'),
    path('vacancies/cat/<str:code>/', ListVacancyViewSub.as_view(), name='vacancies_cat'),
    path('vacancies/<int:pk>/', DetailVacancyView.as_view(), name='vacancies_detail'),
    path('vacancies/<int:pk>/send', ApplicationSend.as_view(), name='application_send'),

    path('companies/<int:pk>/', DetailCompanyView.as_view(), name='companies_detail'),
    path('mycompany/', MyCompanyView.as_view(), name='my_company'),
    path('mycompany/vacancies/', ListMyVacanciesView.as_view(), name='my_vacancies'),
    path('mycompany/vacancies/<int:pk>/', DetailMyVacanciesView.as_view(), name='my_vacancy_detail'),

    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
