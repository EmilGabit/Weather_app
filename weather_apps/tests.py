from django.test import TestCase

# Create your tests here.
class TestWeather_apps(TestCase):

    def test_index(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

