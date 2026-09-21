from django.db import models
from django.contrib.auth.models import User

class CropRecord(models.Model):
    soil_type = models.CharField(max_length=50)
    rainfall_mm = models.FloatField(help_text="Millimeters")
    temperature_c = models.FloatField(help_text="Degrees Celsius")
    humidity_percent = models.FloatField(help_text="Percent")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.soil_type} soil - {self.rainfall_mm}mm, {self.temperature_c}°C"