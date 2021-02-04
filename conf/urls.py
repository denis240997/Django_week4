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
    path('vacancies/send/', ApplicationSendView.as_view(), name='application_send'),

    path('companies/<int:pk>/', DetailCompanyView.as_view(), name='companies_detail'),
    path('mycompany/', MyCompanyEditView.as_view(), name='my_company'),
    path('mycompany/create/', MyCompanyCreateView.as_view(), name='my_company_create'),
    # path('mycompany/vacancies/', ListMyVacanciesView.as_view(), name='my_vacancies'),
    # path('mycompany/vacancies/<int:pk>/', DetailMyVacanciesView.as_view(), name='my_vacancy_detail'),
    #
    path('signin/', SigninView.as_view(), name='signin'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
