from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.urls import reverse

from django.contrib.auth import authenticate, login

from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from job_search.forms import ApplicationForm, RegistrationForm
from job_search.models import Company, Specialty, Vacancy, Application


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(self.request.GET)
        application_form = self.request.session.pop('form', None)
        context['application_form'] = ApplicationForm(application_form)
        self.request.session['vacancy'] = self.object.id
        # if application_form:
        #     context['application_form'] = ApplicationForm(application_form)
        # else:
        #     context['application_form'] = ApplicationForm()
        return context


class DetailCompanyView(DetailView):
    model = Company
    context_object_name = 'company'


class ApplicationSendView(TemplateView):
    template_name = 'job_search/sent.html'

    def post(self, request):
        application_form = ApplicationForm(request.POST)
        vacancy_id = request.session.pop('vacancy')
        if application_form.is_valid():
            application = Application(**application_form.cleaned_data)
            application.vacancy_id = vacancy_id
            if request.user.is_authenticated:
                application.user_id = request.user.id
                application.save()
                return redirect(reverse('application_send'))
            request.session['form'] = request.POST
            return redirect('signin')
        request.session['form'] = request.POST
        return redirect(f'/vacancies/{vacancy_id}/')    # Переделать!!!


# class SignupView(CreateView):
#    form_class = UserCreationForm
#    success_url = 'signin'
#    template_name = 'job_search/authorization/signup.html'
#    # fields = ['name']
#    #     'username',
#    #     'first_name',
#    #     'last_name',
#    #     'password',
#    # ]


class SignupView(TemplateView):
    template_name = 'job_search/authorization/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_form = self.request.session.pop('registration_form', None)
        context['registration_form'] = RegistrationForm(registration_form)
        return context

    def post(self, request):
        registration_form = RegistrationForm(request.POST)
        if registration_form.is_valid():
            user = User.objects.create_user(**registration_form.cleaned_data)
            login(request, user)
            return redirect('signin')
        request.session['registration_form'] = request.POST
        redirect('signup')



class SigninView(LoginView):
    redirect_authenticated_user = True
    template_name = 'job_search/authorization/login.html'
