import pandas as pd
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ml_models.evaluate_models import DATA_PATH, evaluate_random_forest
from .models import CropRecord


class RandomForestAccuracyTests(SimpleTestCase):
    def test_beats_majority_baseline(self):
        # A model that can't beat "always guess the most common crop" isn't learning anything
        results = evaluate_random_forest(pd.read_csv(DATA_PATH))
        self.assertGreater(results['cv_accuracy'], results['baseline_accuracy'])


class SeasonLocationViewTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('farmer', password='x'))

    def test_every_district_gets_a_prediction(self):
        from .views import DISTRICTS
        for district in DISTRICTS:
            response = self.client.get(reverse('season-location-index'), {'district': district})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['predicted_crop'])
            self.assertTrue(0 < response.context['confidence'] <= 100)

    def test_upload_rejects_missing_columns(self):
        csv = SimpleUploadedFile('c.csv', b'soil_type,rainfall_mm\nLoamy,90\n')
        self.client.post(reverse('season-location-upload'), {'csv_file': csv})
        self.assertEqual(CropRecord.objects.count(), 0)
