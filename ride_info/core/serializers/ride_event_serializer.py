from rest_framework import serializers
from core.models.ride_event import RideEvent

class RideEventSerializer(serializers.Serializer):

    created_at = serializers.ReadOnlyField()

    class Meta:
        model = RideEvent
        fields = ('id_ride_event', 'id_ride', 'description', 'created_at')