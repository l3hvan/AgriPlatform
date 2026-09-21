from django.db import models
from django.contrib.auth.models import User

class SensorReading(models.Model):
    district = models.CharField(max_length=50)
    soil_moisture = models.FloatField()
    temperature = models.FloatField(help_text="Degrees Celsius")
    nutrient_level = models.FloatField(help_text="0-100 scale")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.district} - {self.soil_moisture} moisture, {self.temperature}°C"