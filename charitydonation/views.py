import json
import jsonpickle
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash, get_user_model
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from charitydonation.models import Donation, Institution, Category
from charitydonation.forms import SignUpForm, UpdateUserForm, PasswordChangeForm, PasswordChangingForm
from django.contrib import messages
from django.core import serializers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
import datetime
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail, mail_admins
from charitydonation.tokens import account_activation_token
from django.urls import reverse_lazy, reverse
from django.conf import settings


def activate(request, uidb64, token):
    """Generates and sends a token which enables user to activate himself/herself."""
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Aktywacja przebiegla pomyslnie. Mozesz sie zalogowac')
        return redirect('login')
    else:
        messages.error(request, 'Link aktywacyjny wgasl')

    return redirect('landing_page')


def activateEmail(request, user, to_email):
    """Generates and sends email with activation link"""
    mail_subject = "Aktywacja konta"
    message = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'


    })
    email = EmailMessage(mail_subject, message, to=[user])
    if email.send():
        messages.success(request, f'Sprawdz swoja skrzynke {user} i kliknij link aktywacyjny.')
    else:
        messages.error(request, f'Nie udalo sie wyslac wiadomosci na adres {user}')


def register(request):
    """Creates a new inactive user."""
    context = {}
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            new_user = authenticate(username=username, password=password)

            if new_user is not None:
                messages.error(request, 'Rejestracja przebiegła pomyślnie. Możesz zalogować się na swoje konto')
                login(request, new_user)
                return redirect('login')
        else:
            context['form'] = form
    else:
        form = SignUpForm()
        context['form'] = form
    return render(request, 'register.html', context)


class LandingPage(View):
    """
    Displays total donated bags and number of institutions which received donations. Also, it displays
    first page of every type paginated institutions. The rest of pages are dynamically loaded, without page reload,
    with the use of JavaScript.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_super"] = self.request.user.is_superuser
        return context

    def get(self, request):

        institutions = Institution.objects.filter(type=1).order_by('-id').distinct()
        institutions2 = Institution.objects.filter(type=2).order_by('-id').distinct()
        institutions3 = Institution.objects.filter(type=3).order_by('-id').distinct()
        page = request.GET.get('page', 1)
        page2 = request.GET.get('page', 1)
        page3 = request.GET.get('page', 1)
        paginator = Paginator(institutions, 4)
        paginator2 = Paginator(institutions2, 4)
        paginator3 = Paginator(institutions3, 4)
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
                      {'donation': donation, 'i': i, 'q': q, 'institutions': institutions,
                       'institutions2': institutions2, 'institutions3': institutions3,
                       })


class JsonLanding(View):
    """
    Dynamically displays total amount of donated bags
    """
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            donation = Donation.objects.all()
            don = sum(donation.values_list('quantity', flat=True))
            return JsonResponse({'don': don})
            pass
        return JsonResponse({'message': "Wrong validation"})


class DonationView(View):
    """
    Renders confirmation info about realized donation.
    """

    def get(self, request):
        return render(request, "form-confirmation.html")


class UserProfile(LoginRequiredMixin, View):
    """
    Displays user profile with details information.
    """
    login_url = '/login/'

    def get(self, request):
        donations = Donation.objects.filter(user=request.user)
        return render(request, 'user-profile.html', {'donations': donations})


class UserDonation(LoginRequiredMixin, View):
    """
    Displays users donations with details. Allows user to update donation status.
    """
    login_url = '/login/'

    def get(self, request):
        today = datetime.date.today()
        donations = Donation.objects.filter(user=request.user).order_by('-is_taken', '-pick_up_date').reverse()
        return render(request, 'my-donations.html', {'donations': donations, 'today': today})

    def post(self, request):
        today = datetime.date.today()
        is_taken = request.POST.get('is_taken')
        print(is_taken)
        donations = Donation.objects.filter(user=request.user).order_by('-is_taken', '-pick_up_date').reverse()
        id_list = request.POST.getlist('ids')
        donations.update(is_taken=False)
        for i in id_list:
            Donation.objects.filter(pk=int(i)).update(is_taken=True)

        return render(request, 'my-donations.html', {'donations': donations, 'today': today})


@login_required(login_url='/login')
def donation_add_view(request):
    """
    Multiple step donation form.
    """
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
    """
    Dynamically filtering institutions by chosen categories.
    """
    categories = request.GET.getlist('category[]')
    pick_up_date = request.GET.getlist('pick_up_date[]')
    institutions = Institution.objects.all().order_by('-id').distinct()
    if len(categories) > 0:
        institutions = Institution.objects.filter(categories__in=categories).annotate(count=Count('categories')). \
            filter(count=len(categories))

    t = render_to_string('institution-list.html', {'data': institutions})
    print(institutions)
    return JsonResponse({'data': t})


class Login(View):
    """
    After successful authentication redirect to landing page.
    """
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
            messages.error(request, 'Uzytkownik o takiej nazwie nie istnieje. Zarejestruj sie.')
            return redirect('register')
        messages.error(request, 'Podane haslo jest niepoprawne.')
        return render(request, 'login.html')


class LogoutView(LoginRequiredMixin, View):
    """
    Redirect to main page after logout.
    """
    def get(self, request):
        logout(request)
        return redirect('landing_page')


@login_required(login_url='/login')
def update_profile(request):
    """
    Allows user to update their profile.
    """
    if request.method == "POST":
        password = request.POST.get('password')
        user = authenticate(request, username=request.user.username, password=password)
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user is not None:
            if user_form.is_valid():
                print(request.user.password)
                user_form.save()
                messages.success(request, 'Profil zostal zakutalizowany')
                return redirect('profile')
        if password == '':
            messages.error(request, 'Aby zaktualizowac dane konieczne jest podanie hasla!')
        else:
            messages.error(request, 'Wprowadzone haslo jest niepoprawne!')

    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': user_form})


def change_password(request):
    """
    Allows user to change their password. Requires old password.
    """
    if request.POST:
        form = PasswordChangingForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Haslo zostalo zaktualizowane!')
            return redirect('profile')
        else:
            messages.error(request, "Wystapil problem ze zmianą hasła")
    else:
        form = PasswordChangingForm(request.user)
    return render(request, 'change_password.html', {'form':form})


def passwordReset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(username=user_email)).first()
            if associated_user:
                subject = "Resetuj haslo"
                message = render_to_string("reset_password_confirmation.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.username])
                if email.send():
                    messages.success(request,
                                     """
                                     Zresetowales haslo!
                                     
                                         Jesli podany przez Ciebie email jest polaczony z kontem w serwisie, otrzymasz maila z instrukcja resetu hasla. 
                                         Wkrotce powinienes otrzymac maila.<br>Jesli wiadomosc sie nie pojawi sprawdz poprawnosc wprowadzonego adresu i sprawdz folder spam.
                                     
                                     """
                                     )
                else:
                    messages.error(request, "Wystapil problem z resetem hasla, <b>SERVER PROBLEM</b>")
            else:
                messages.error(request, "Nie ma konta powiazanego z tym adresem email")

            return redirect('login')

    form = PasswordResetForm
    return render(request=request,
                  template_name='reset_password.html',
                  context={'form':form})

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Haslo zostalo zmienione. Mozesz sie zalogowac.')
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'reset_password_con.html', {'form':form})

    else:
        messages.error(request, 'Link resetujacy wygasl')
    messages.error(request, 'Cos poszlo nie tak, przekierowanie na strone glowna.')
    return redirect('landing_page')


def contact_form(request):
    if request.method == 'POST':
        sender_name = request.POST['name']
        sender_last_name = request.POST['surname']
        message = request.POST['message']
        user_email = request.user.email
        admin = User.objects.filter(is_superuser=True)
        print(admin)
        send_mail(
            sender_name,
            message,
            user_email,
            admin
        )
        return render(request, 'contact.html', {'message':message})
    else:
        return render(request, 'contact.html')


