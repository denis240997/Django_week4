from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User

from job_search.models import Company, Specialty, Vacancy, Application
from job_search.forms import ApplicationForm


class MainView(TemplateView):
    template_name = 'job_search/index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['specialty_list'] = Specialty.objects.annotate(vac_count=Count('vacancies'))
        context['company_list'] = Company.objects.annotate(vac_count=Count('vacancies'))
        return context


class ListVacancyViewAll(ListView):
    model = Vacancy
    context_object_name = 'vacancy_list'
    queryset = Vacancy.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все вакансии'
        context['count'] = len(self.queryset) if self.queryset else 0
        return context


class ListVacancyViewSub(ListView):
    model = Vacancy
    context_object_name = 'vacancy_list'

    def get_queryset(self, **kwargs):
        # Придумать как не аннотировать все, это излишне
        self.specialty = get_object_or_404(Specialty.objects.annotate(vac_count=Count('vacancies')),
                                           code=self.kwargs['code'])
        return self.specialty.vacancies.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.specialty.title
        context['count'] = self.specialty.vac_count
        return context


class DetailVacancyView(DetailView):
    # А тут как уменьшить количество запросов???
    model = Vacancy
    context_object_name = 'vacancy'


class DetailCompanyView(DetailView):
    model = Company
    context_object_name = 'company'


class ApplicationSend(View):

    def post(self, request):
        application_form = ApplicationForm(request.POST)
        if application_form.is_valid():
            appl_data = application_form.cleaned_data
            appl_data['vacancy'] = get_object_or_404(Vacancy, id=appl_data['vacancy'])
            Application.objects.create(user=User.objects.all().first(), **appl_data)
        return redirect('/')                                  # Переделать!!!


# class TestView(TemplateView):
#     template_name = 'job_search/form.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(TestView, self).get_context_data()
#         context['postcard_form'] = PostcardForm()
#         return context
#
#     def post(self, request, *args, **kwargs):
#         postcard_form = PostcardForm(request.POST)
#         if postcard_form.is_valid():
#             print("Haha ty pidor")
#             print(postcard_form.data.get('date_of_delivery'))
#         else:
#             print("Haha ty PIDORAS")
#         return redirect('/test')
