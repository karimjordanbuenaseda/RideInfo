from rest_framework import serializers
from core.models.ride import Ride
from core.serializers.ride_event_serializer import RideEventSerializer
from core.serializers.user_serializers import UserSerializer

class RideSerializer(serializers.Serializer):

    rider = UserSerializer(source='id_rider', read_only=True)
    driver = UserSerializer(source='id_driver', read_only=True)
    # todays_ride_events = serializers.SerializerMethodField()
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Ride
        fields = (
            'id_ride',
            'status',
            'rider',
            'driver',
            'pickup_latitude', 
            'pickup_longitude',
            'dropoff_latitude', 
            'dropoff_longitude',
            'pickup_time',
            'distance_to_pickup'
        )

    # def get_todays_ride_events(self, obj):
    #     return RideEventSerializer(obj.prefetched_todays_events, many=True).data