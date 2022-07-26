"""portfolio_lab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from charitydonation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.LandingPage.as_view(), name='landing_page'),
    path('data/', views.JsonLanding.as_view(), name='data'),
    path('add_donation/', views.donation_add_view, name='add_donation'),
    path('summary/', views.DonationView.as_view(), name='summary'),
    path('filter-data/', views.filter_data, name='filter-data'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('password/', views.change_password, name='password'),
    path('donations/', views.UserDonation.as_view(), name='donation'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password_reset/', views.passwordReset, name='password_reset'),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirmation'),
    path('contact/', views.contact_form, name='contact'),



]
