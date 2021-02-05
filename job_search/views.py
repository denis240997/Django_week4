from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.urls import reverse

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from job_search.forms import ApplicationForm, RegistrationForm, CompanyEditForm
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
    model = Vacancy
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_form = self.request.session.get(f'form_{self.object.id}', None)
        context['application_form'] = ApplicationForm(application_form)
        self.request.session['vacancy'] = self.object.id
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
            request.session[f'form_{vacancy_id}'] = request.POST
            return redirect('signin')
        request.session[f'form_{vacancy_id}'] = request.POST
        return redirect(f'/vacancies/{vacancy_id}/')  # Переделать!!!


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
        return redirect('signup')


class SigninView(LoginView):
    redirect_authenticated_user = True
    template_name = 'job_search/authorization/login.html'


def logout_view(request):
    logout(request)
    return redirect('main')


# @login_required
class MyCompanyEditView(DetailView):
    template_name = 'job_search/authorized_interface/company_edit.html'

    def set_object(self, request):
        try:
            self.object = Company.objects.get(owner__id=request.user.id)
        except Company.DoesNotExist:
            self.object = None

    def get(self, request, *args, **kwargs):
        self.set_object(request)
        if self.object is None and not request.session.pop('create_company', False):
            return redirect('my_company_create')
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_content = self.request.session.pop('company_form', None)
        context['company_form'] = CompanyEditForm(form_content if form_content else self.object.__dict__)
        context['updated'] = self.request.session.pop('updated', False)
        return context

    def post(self, request):
        self.set_object(request)
        form_content = request.POST, request.FILES
        company_form = CompanyEditForm(*form_content)
        if company_form.is_valid():
            if self.object:
                print(self.object)
                for attr, value in company_form.cleaned_data.items():
                    setattr(self.object, attr, value)
            else:
                self.object = Company(**company_form.cleaned_data)
                self.object.owner_id = request.user.id
            self.object.save()
            request.session['updated'] = True
            return redirect('my_company')
        request.session['company_form'] = form_content[0]
        return redirect('my_company')


# @login_required
class MyCompanyCreateView(TemplateView):
    template_name = 'job_search/authorized_interface/company_create.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        request.session['create_company'] = True
        return self.render_to_response(context)
