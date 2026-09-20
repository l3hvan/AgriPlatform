from django.db import models
from django.contrib.auth.models import User

class SeedRecord(models.Model):
    district = models.CharField(max_length=50)
    year = models.IntegerField()
    seed_variety = models.CharField(max_length=100)
    yield_t_ha = models.FloatField(help_text="Tonnes per hectare")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.district} {self.year} - {self.seed_variety}"