from django.db import models

class User(models.Model):

    ROLE_CHOICES = (
            ('admin', 'Admin'),
            ('driver', 'Driver'),
            ('rider', 'Rider'),
    )
    
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
