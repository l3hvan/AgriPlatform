from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import WeatherLog


class DashboardTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('farmer', password='x'))

    def test_empty_dashboard(self):
        response = self.client.get(reverse('home-index'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_data'])

    def test_upload_then_dashboard_shows_latest(self):
        csv = SimpleUploadedFile(
            'w.csv', b'date,temperature,humidity,soil_moisture\n2026-01-01,20,60,30\n2026-01-02,25,55,28\n'
        )
        self.client.post(reverse('home-upload'), {'csv_file': csv})
        self.assertEqual(WeatherLog.objects.count(), 2)

        response = self.client.get(reverse('home-index'))
        self.assertEqual(response.context['temperature'], 25)

    def test_models_page_shows_all_three_logics(self):
        response = self.client.get(reverse('models-overview'))
        self.assertEqual(response.status_code, 200)
        for heading in ('Random Forest', 'K-Nearest Neighbors', 'Fuzzy Logic'):
            self.assertContains(response, heading)
        self.assertGreater(response.context['rf']['cv_accuracy'], response.context['rf']['baseline_accuracy'])

    def test_upload_rejects_missing_columns(self):
        csv = SimpleUploadedFile('w.csv', b'date,temperature\n2026-01-01,20\n')
        self.client.post(reverse('home-upload'), {'csv_file': csv})
        self.assertEqual(WeatherLog.objects.count(), 0)
