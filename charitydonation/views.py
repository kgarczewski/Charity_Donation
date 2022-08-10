import json
import jsonpickle

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm
from charitydonation.models import Donation, Institution, Category
from charitydonation.forms import SignUpForm
from django.contrib import messages
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string


# Create your views here.


class LandingPage(View):
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
                      {'donation': donation, 'i': i, 'q': q, 'institutions': institutions, 'institutions2':institutions2, 'institutions3':institutions3})


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

# # class AddDonation(View):
#     def get(self, request):
#         category = Category.objects.all()
#         query = request.POST.get("categories")
#         qs = Institution.objects.all()
#         return render(request, 'form.html', {'category': category, 'queryset': qs})
# #
# #     def post(self, request):
# #         if request.POST.get('action') == 'create-post':
# #             bags = request.POST.get('bags')
# #             organization = request.POST.get('organization')
# #             print(organization)
# #
# #             Donation.objects.create(
# #                 quantity=bags,
# #                 institution=organization
# #                     )
# #         return HttpResponse('udalo sie')


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
        new_donation.categories.add(request.POST['categories'])
        new_donation.user = request.user

        return HttpResponse(
            json.dumps(json.loads(jsonpickle.encode(new_donation))),
            content_type="application/json"
        )
    quantity = request.POST.get('bags')
    print(quantity)
    category = Category.objects.all()
    query = request.POST.get("categories")
    qs = Institution.objects.all()
    pick_up_date = request.GET.getlist('pick_up_date[]')
    pick_up_comment = request.GET.get('pick_up_comment', 'es')

    return render(request, 'form.html', {'category': category, 'queryset': qs, 'pick_up_date': pick_up_date,
                                         'quantity': quantity, 'comment': pick_up_comment})


# class JsonAddDonation(View):
#     def get(self, request, *args, **kwargs):
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             filter = self.request.GET.get("categories")
#             print(self.request.GET.get("filter_category"))
#             queryset = Institution.objects.all()
#             print(queryset)
#             queryset_filtered = queryset.filter()
#             return JsonResponse({'queryset':queryset})
#         return JsonResponse({'message': "Wrong validation"})


def filter_data(request):
    categories = request.GET.getlist('category[]')
    print(categories)
    pick_up_date = request.GET.getlist('pick_up_date[]')
    print(pick_up_date)
    institutions = Institution.objects.all().order_by('-id').distinct()
    if len(categories)>0:
        institutions = Institution.objects.annotate(count=Count('categories')).filter(count=len(categories))
        for id in categories:
            institutions = institutions.filter(categories__id=id)
    t = render_to_string('institution-list.html', {'data': institutions})
    print(institutions)
    return JsonResponse({'data': t})


# def summary(request):
#     inst = request.GET.getlist('org[]')
#     print(inst)
#     t = render_to_string('summary.html', {'data': inst})
#     return JsonResponse({'data': t})
#


class Register(View):

    def get(self, request):
        form = SignUpForm(request.POST)
        return render(request, 'register.html', {'form':form})

    def post(self, request):
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
        return render(request, 'register.html')


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


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('landing_page')




