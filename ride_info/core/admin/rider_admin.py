from django.contrib import admin
from core.models.ride import Ride

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    model = Ride
    list_display = ('id_ride', 'id_driver', 'id_rider', 'status')
    list_filter = ('status',)