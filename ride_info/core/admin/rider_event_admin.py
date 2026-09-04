from django.contrib import admin
from core.models.ride_event import RideEvent

@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    model = RideEvent
    list_display = ('id_ride_event', 'id_ride', 'description', 'created_at')
    search_fields = ('description',)
    list_filter = ('id_ride',)
    ordering = ('-id_ride_event',)