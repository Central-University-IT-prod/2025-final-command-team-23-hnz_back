from rest_framework import status
from rest_framework.test import APITestCase
from .models import Client
from .serializers import ClientSerializer

class ClientAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/client/register/"

    def test_create_client(self):
        data = {
            'id': 1,
            'first_name': 'Иван Иванов'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(Client.objects.get().first_name, 'Иван Иванов')

    def test_create_client_with_invalid_data(self):
        data = {
            'id': 'invalid_id',
            'first_name': ''
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Client.objects.count(), 0)


class SerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_remove = ["id", "first_name"]
        self.good_data = {
            'id': 1,
            "first_name": "Клиентик"
        }

    def test_not_full_data(self):
        for i in self.keys_for_remove:
            self.for_check = self.good_data.copy()
            del self.for_check[i]
            self.assertFalse(ClientSerializer(data=self.for_check).is_valid())
