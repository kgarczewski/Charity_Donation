from django.contrib import admin
from charitydonation.models import Donation, Institution, Category
# Register your models here.
admin.site.register(Donation)
admin.site.register(Institution)
admin.site.register(Category)
