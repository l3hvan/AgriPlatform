import pandas as pd
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from ml_models.evaluate_models import DATA_PATH, evaluate_knn
from .models import SeedRecord


class KnnAccuracyTests(SimpleTestCase):
    def test_overall_error_stays_reasonable(self):
        # Currently ~32%. Guard against a change that makes yield estimates much worse.
        results = evaluate_knn(pd.read_csv(DATA_PATH))
        self.assertLess(results['overall_error'], 40)


class GrainsPlantsViewTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('farmer', password='x'))

    def test_every_district_gets_an_estimate(self):
        from .views import DISTRICTS
        for district in DISTRICTS:
            response = self.client.get(reverse('grains-plants-index'), {'district': district})
            self.assertEqual(response.status_code, 200)
            self.assertGreater(response.context['estimated_yield'], 0)
            self.assertLessEqual(len(response.context['similar_seasons']), 3)

    def test_upload_rejects_non_csv(self):
        upload = SimpleUploadedFile('seeds.txt', b'district,year,seed_variety,yield_t_ha\n')
        self.client.post(reverse('grains-plants-upload'), {'csv_file': upload})
        self.assertEqual(SeedRecord.objects.count(), 0)
