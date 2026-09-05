from rest_framework import serializers
from core.models.ride import Ride
from core.serializers.ride_event_serializer import RideEventSerializer
from core.serializers.user_serializers import UserSerializer

class RideSerializer(serializers.ModelSerializer):

    rider = UserSerializer(source='id_rider', read_only=True)
    driver = UserSerializer(source='id_driver', read_only=True)
    todays_ride_events = RideEventSerializer(many=True, read_only=True)
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Ride
        fields = (
            'id_ride',
            'status',
            'rider',
            'driver',
            'todays_ride_events',
            'pickup_latitude', 
            'pickup_longitude',
            'dropoff_latitude', 
            'dropoff_longitude',
            'pickup_time',
            'distance_to_pickup'
        )