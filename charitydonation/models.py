from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin


# Create your models here.


class MyUserAdmin(UserAdmin):

    def has_delete_permission(self, request, obj=None):

        if User.objects.filter(is_superuser=True).count() > 1:
            return True
        if obj == request.user:
            return False
        return False


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Institution(models.Model):
    types = [
        (1, 'fundacja'),
        (2, 'organizacja pozarządowa'),
        (3, 'zbiórka lokalna')
    ]
    name = models.CharField(max_length=250)
    description = models.TextField()
    type = models.IntegerField(choices=types, default='fundacja')
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    def get_categories(self):
        if self.categories:
            return '%s' % " / ".join([categories.name for categories in self.categories.all()])


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=9)
    city = models.CharField(max_length=250)
    zip_code = models.CharField(max_length=5)
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    is_taken = models.BooleanField('Odebrany', default=False)

    def __str__(self):
        return self.pick_up_comment

    def get_categories(self):
        return ', '.join([a.name for a in self.categories.all()])


