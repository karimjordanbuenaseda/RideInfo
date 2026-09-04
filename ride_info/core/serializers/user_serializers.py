from rest_framework import serializers
from core.models.user import User

class UserSerializer(serializers.Serializer):

    class Meta:
        model = User
        fields = (
            'id_user',
            'role',
            'first_name',
            'last_name',
            'email',
            'phone_number'
        )