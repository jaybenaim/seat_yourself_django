from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.core import validators 




# def validate_reservation_time(value): 
#     if value >= restaurant.closing_time - timedelta(hours=1):
#         raise ValidationError(_('You can not book that time - %(value). A bit too close to closing time. Try a little earlier. '), 
#         params={
#             'value': value
#         } )

class Profile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True)
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @classmethod
    def exists_for_user(self, user):
        return Profile.objects.filter(user_id=user.id).exists()


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def image(self):
        return self.restaurants.all()[0].image

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_restaurants')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='restaurants')
    guests = models.ManyToManyField(User, through='Reservation', related_name='reserved_restaurants')
    name = models.CharField(max_length=255)
    capacity = models.IntegerField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    image = models.URLField(max_length=255, null=True)
    description = models.TextField(null=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.name

    def open_past_midnight(self):
        return self.closing_time < self.opening_time

    def room_for(self, date, time, number_of_people):
        reserved_seats = self.reservations.filter(date=date, time=time).aggregate(Sum('party_size'))
        reserved_seats = reserved_seats['party_size__sum'] or 0
        return (reserved_seats + number_of_people) <= self.capacity

class Reservation(models.Model):
    user = models.ForeignKey(User, related_name='reservations_made', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='reservations', on_delete=models.CASCADE)
    party_size = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return "{} {} - party of {}".format(self.date, self.time, self.party_size)

    def date_and_time(self):
        date = self.date.strftime("%Y-%m-%d")
        time = self.time.strftime("%H:%M")
        return "{} {}".format(date, time)
