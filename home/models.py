from django.db import models
from django.contrib.auth.models import User

class WeatherLog(models.Model):
    date = models.DateField()
    temperature = models.FloatField(help_text="Degrees Celsius")
    humidity = models.FloatField(help_text="Percent")
    soil_moisture = models.FloatField(help_text="Percent")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.temperature}°C"