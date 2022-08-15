import json
import jsonpickle
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from charitydonation.models import Donation, Institution, Category
from charitydonation.forms import SignUpForm, UpdateUserForm
from django.contrib import messages
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string


# Create your views here.


class LandingPage(View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_super"] = self.request.user.is_superuser
        return context
    def get(self, request):

        institutions = Institution.objects.filter(type=1).order_by('-id').distinct().values()
        institutions2 = Institution.objects.filter(type=2).order_by('-id').distinct()
        institutions3 = Institution.objects.filter(type=3).order_by('-id').distinct()
        page = request.GET.get('page', 1)
        page2 = request.GET.get('page', 1)
        page3 = request.GET.get('page', 1)
        paginator = Paginator(institutions, 2)
        paginator2 = Paginator(institutions2, 2)
        paginator3 = Paginator(institutions3, 2)
        donation = Donation.objects.all()
        q = sum(donation.values_list('quantity', flat=True))
        i = Donation.objects.values('institution').annotate(instituiton=Count('institution')).order_by('institution')
        try:
            institutions = paginator.page(page)
            institutions2 = paginator2.page(page2)
            institutions3 = paginator3.page(page3)

        except PageNotAnInteger:
            institutions = paginator.page(1)
            institutions2 = paginator2.page(1)
            institutions3 = paginator3.page(1)
        except EmptyPage:
            institutions = paginator.page(paginator.num_pages)
            institutions2 = paginator2.page(paginator2.num_pages)
            institutions3 = paginator3.page(paginator3.num_pages)

        return render(request, "index.html",
                      {'donation': donation, 'i': i, 'q': q, 'institutions': institutions, 'institutions2':institutions2, 'institutions3':institutions3,
                       })


class JsonLanding(View):
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            donation = Donation.objects.all()
            don = sum(donation.values_list('quantity', flat=True))
            return JsonResponse({'don':don})
            pass
        return JsonResponse({'message': "Wrong validation"})


class DonationView(View):
    def get(self, request):
        return render(request, "form-confirmation.html")


class UserProfile(View):
    def get(self, request):
        donations = Donation.objects.filter(user=request.user)
        return render(request, 'user-profile.html', {'donations': donations})


class UserDonation(View):
    def get(self, request):
        donations = Donation.objects.filter(user=request.user).order_by('-pick_up_date').reverse()
        return render(request, 'my-donations.html', {'donations': donations})


@login_required(login_url='/login')
def donation_add_view(request):
    if request.method == 'POST':
        quantity = request.POST['quantity']
        inst = request.POST['institution']
        institution = Institution.objects.get(id=inst)
        user = request.user
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        city = request.POST['city']
        zip_code = request.POST['zip_code']
        pick_up_date = request.POST['pick_up_date']
        pick_up_time = request.POST['pick_up_time']
        pick_up_comment = request.POST['pick_up_comment']
        new_donation = Donation(
            user=user,
            quantity=quantity,
            institution=institution,
            address=address,
            phone_number=phone_number,
            city=city,
            zip_code=zip_code,
            pick_up_date=pick_up_date,
            pick_up_time=pick_up_time,
            pick_up_comment=pick_up_comment,
        )
        new_donation.save()
        new_donation.user = request.user
        for i in request.POST.getlist('categories'):
            new_donation.categories.add(i)

        return HttpResponse(
            json.dumps(json.loads(jsonpickle.encode(new_donation))),
            content_type="application/json"
        )
    categories = request.GET.getlist('category[]')
    print(categories)
    quantity = request.GET.getlist('bags[]')
    print(quantity)
    category = Category.objects.all()
    qs = Institution.objects.all()
    pick_up_date = request.GET.getlist('pick_up_date[]')
    pick_up_comment = request.GET.get('pick_up_comment', 'es')

    return render(request, 'form.html', {'category': category, 'queryset': qs, 'pick_up_date': pick_up_date,
                                         'quantity': quantity, 'comment': pick_up_comment, 'categories': categories})


def filter_data(request):
    categories = request.GET.getlist('category[]')
    pick_up_date = request.GET.getlist('pick_up_date[]')
    institutions = Institution.objects.all().order_by('-id').distinct()
    if len(categories)>0:
        institutions = Institution.objects.annotate(count=Count('categories')).filter(count=len(categories))
        for id in categories:
            institutions = institutions.filter(categories__id=id)
    t = render_to_string('institution-list.html', {'data': institutions})
    print(institutions)
    return JsonResponse({'data': t})



def Register(request):
    context = {}
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            form.save()
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
                return redirect('login')
        else:
            context['form'] = form
    else:
        form = SignUpForm()
        context['form'] = form
    return render(request, 'register.html', context)


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing_page')
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Haslo albo nazwa uzytkownika jest nieprawidlowe')
            return render(request, 'register.html', )
        return render(request, 'login.html')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('landing_page')


# class UpdateProfile(LoginRequiredMixin, UserCreationForm):
#     model = User
#     template_name = 'update_profile.html'
#     fields = ['username', 'first_name', 'last_name']
#     success_url = '/profile'

def update_profile(request):

    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profil zostal zakutalizowany')
            return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'update_profile.html', {'form':user_form})


# class ChangePassword(LoginRequiredMixin, View):
#     def post(self, request):
#         form = PasswordChangeForm(request.user, request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # Important!
#             messages.success(request, 'Your password was successfully updated!')
#             return redirect('profile')
#         else:
#             messages.error(request, 'Please correct the error below.')
#             return redirect('password')
#
#     def get(self, request):
#         form = PasswordChangeForm(request.user)
#         return render(request, 'change_password.html', {
#                             'form': form
#                  })
def change_password(request):

    context = {}
    if request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            context['form'] = form
    else:
        form = PasswordChangeForm(request.user)
        context['form'] = form
    return render(request, 'change_password.html', context)

