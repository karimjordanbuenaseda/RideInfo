from django.db import models

from core.models.user import User

class Ride(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('en-route', 'En-route'),
        ('pickup', 'Pickup'),
        ('dropoff', 'Dropoff'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    id_rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_rider')
    id_driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_as_driver')
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def __str__(self):
        return f"Ride {self.id_ride}: {self.status} - {self.id_rider} with {self.id_driver}"