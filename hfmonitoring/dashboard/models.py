from djongo import models
from bson import ObjectId
from djongo.models import DjongoManager

class Vitals(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    weight = models.FloatField()
    height = models.IntegerField()
    systolic_bp = models.IntegerField()
    diastolic_bp = models.IntegerField()
    heart_rate = models.IntegerField()
    oxygen_saturation = models.IntegerField()

    class Meta:
        abstract = True  # Embedded model

class Patient(models.Model):
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, default="Not Specified")
    date_of_birth = models.DateField(null=True, blank=True)
    contacts = models.JSONField()  # Example: {"phone": "+123456789", "email": "john@example.com"}
    vitals = models.ArrayField(
        model_container=Vitals
    )  # Embedded Vitals

    objects = DjongoManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "patients"
