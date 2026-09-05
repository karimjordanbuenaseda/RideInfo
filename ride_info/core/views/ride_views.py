from datetime import timedelta

from django.db.models import F, FloatField, ExpressionWrapper, Prefetch, Value
from django.db.models.functions import ASin, Cos, Radians, Sin, Sqrt
from django.utils import timezone
from rest_framework import viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.models import *
from core.serializers import *


def annotate_distance_to_pickup(queryset, latitude, longitude):
    lat = Value(float(latitude))
    lng = Value(float(longitude))

    d_lat = Radians(F('pickup_latitude') - lat)
    d_lng = Radians(F('pickup_longitude') - lng)

    a = (
        Sin(d_lat / Value(2.0)) * Sin(d_lat / Value(2.0))
        + Cos(Radians(lat)) * Cos(Radians(F('pickup_latitude')))
        * Sin(d_lng / Value(2.0)) * Sin(d_lng / Value(2.0))
    )

    distance_km = 6371.0 * 2.0 * ASin(Sqrt(a))

    return queryset.annotate(
        distance_to_pickup=ExpressionWrapper(distance_km, output_field=FloatField())
    )


class RideViewSet(viewsets.ViewSet):

    def list(self, request):
        cutoff = timezone.now() - timedelta(hours=24)
        todays_events = Prefetch(
            'ride_events',
            queryset=RideEvent.objects.filter(created_at__gte=cutoff).order_by('created_at'),
            to_attr='todays_ride_events',
        )

        queryset = (
            Ride.objects
            .select_related('id_rider', 'id_driver')
            .prefetch_related(todays_events)
        )

        # filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # filter by rider email
        email = self.request.query_params.get('rider_email', None)
        if email:
            try:
                user = User.objects.get(email=email)
                queryset = queryset.filter(id_rider=user.id_user)
            except User.DoesNotExist:
                queryset = Ride.objects.none()

        # sorting
        sort = self.request.query_params.get('sort', None)
        if sort == 'pickup_time':
            queryset = queryset.order_by('pickup_time')
        elif sort == '-pickup_time':
            queryset = queryset.order_by('-pickup_time')
        elif sort in ('distance', '-distance'):
            latitude = self.request.query_params.get('latitude')
            longitude = self.request.query_params.get('longitude')
            if latitude is None or longitude is None:
                return Response(
                    {'detail': "Query params 'latitude' and 'longitude' are required when sorting by distance."},
                    status=400,
                )
            try:
                lat, lng = float(latitude), float(longitude)
            except ValueError:
                return Response(
                    {'detail': "'latitude' and 'longitude' must be valid numbers."},
                    status=400,
                )
            queryset = annotate_distance_to_pickup(queryset, lat, lng)
            direction = '-distance_to_pickup' if sort == '-distance' else 'distance_to_pickup'
            queryset = queryset.order_by(direction)
        else:
            queryset = queryset.order_by('id_ride')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = 'page_size'
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = RideSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RideSerializer(queryset, many=True)

        return Response(serializer.data)