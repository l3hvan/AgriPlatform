from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ml_models.fuzzy_logic import compute_fertilizer, compute_irrigation, trimf
from .models import SensorReading


class TrimfTests(SimpleTestCase):
    def test_peak_and_edges(self):
        self.assertEqual(trimf(5, 0, 5, 10), 1.0)
        self.assertEqual(trimf(0, 0, 5, 10), 0.0)
        self.assertEqual(trimf(10, 0, 5, 10), 0.0)
        self.assertAlmostEqual(trimf(2.5, 0, 5, 10), 0.5)

    def test_shoulders_stay_fully_in_set(self):
        # Left shoulder (a == b) and right shoulder (b == c) must not drop to 0 at or beyond the edge
        self.assertEqual(trimf(15, 15, 15, 25), 1.0)
        self.assertEqual(trimf(5, 15, 15, 25), 1.0)
        self.assertEqual(trimf(45, 30, 45, 45), 1.0)
        self.assertEqual(trimf(50, 30, 45, 45), 1.0)


class IrrigationLogicTests(SimpleTestCase):
    def test_never_zero_at_extremes(self):
        # Regression: 45C on dry soil used to return 0 minutes
        for soil_moisture in (71, 200, 446):
            for temperature in (15, 45):
                self.assertGreater(compute_irrigation(soil_moisture, temperature), 0)

    def test_dry_soil_needs_more_water_than_wet(self):
        for temperature in (15, 22, 28, 36, 45):
            self.assertGreater(compute_irrigation(80, temperature), compute_irrigation(400, temperature))

    def test_hot_needs_more_water_than_cool(self):
        for soil_moisture in (80, 200, 400):
            self.assertGreater(compute_irrigation(soil_moisture, 42), compute_irrigation(soil_moisture, 16))

    def test_output_within_duration_range(self):
        for soil_moisture in (0, 71, 150, 300, 446, 600):
            for temperature in (0, 20, 30, 50):
                self.assertTrue(0 <= compute_irrigation(soil_moisture, temperature) <= 30)


class FertilizerLogicTests(SimpleTestCase):
    def test_actions(self):
        self.assertEqual(compute_fertilizer(10), 'Apply nitrogen now')
        self.assertEqual(compute_fertilizer(50), 'Light application recommended')
        self.assertEqual(compute_fertilizer(90), 'No fertilizer needed')


class ScheduleViewTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('farmer', password='x'))

    def test_index_shows_recommendation(self):
        response = self.client.get(reverse('schedule-index'), {'district': 'Banda', 'temperature': 45})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.context['irrigation_minutes'], 0)

    def test_uses_latest_uploaded_sensor_reading(self):
        SensorReading.objects.create(district='Banda', soil_moisture=400, temperature=20, nutrient_level=90)
        response = self.client.get(reverse('schedule-index'), {'district': 'Banda'})
        self.assertEqual(response.context['soil_moisture'], 400)
        self.assertEqual(response.context['temperature'], 20)
        self.assertEqual(response.context['fertilizer_action'], 'No fertilizer needed')

    def test_falls_back_to_satellite_without_upload(self):
        response = self.client.get(reverse('schedule-index'), {'district': 'Banda'})
        self.assertIsNone(response.context['sensor_reading'])
        self.assertEqual(response.context['soil_moisture'], 147.0)

    def test_upload_rejects_missing_columns(self):
        csv = SimpleUploadedFile('s.csv', b'district,soil_moisture\nBanda,150\n')
        self.client.post(reverse('schedule-upload'), {'csv_file': csv})
        self.assertEqual(SensorReading.objects.count(), 0)

    def test_upload_saves_valid_rows(self):
        csv = SimpleUploadedFile(
            's.csv', b'district,soil_moisture,temperature,nutrient_level\nBanda,150,30,40\nSagar,200,25,60\n'
        )
        self.client.post(reverse('schedule-upload'), {'csv_file': csv})
        self.assertEqual(SensorReading.objects.count(), 2)


class LoginRequiredTests(TestCase):
    def test_redirects_anonymous_user(self):
        response = self.client.get(reverse('schedule-index'))
        self.assertEqual(response.status_code, 302)
