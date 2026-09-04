from rest_framework import viewsets
from rest_framework.response import Response

from core.models import *
from core.serializers import *

class RideViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Ride.objects.select_related('id_rider', 'id_driver')

        serializer = RideSerializer(queryset, many=True)
        return Response(serializer.data)