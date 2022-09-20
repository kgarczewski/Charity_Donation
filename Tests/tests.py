from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse
# Create your tests here.
# class URLTest(TestCase):
#     def test_homepage(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)


@pytest.mark.django_db
def test_landingpage(client):
    url = reverse('landing_page')
    response = client.get(url)
    assert response.status_code == 200