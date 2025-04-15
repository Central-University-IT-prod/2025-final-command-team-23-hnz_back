from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from companies.models import Company
from companies.serializers import CompanySerializer
import pytest


@pytest.mark.django_db
class CompanyTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/company/"

    def test_create_company(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.05,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Company.objects.filter(id=response.data["company_id"]).exists())

    def test_login_company(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.05,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        self.client.post(self.url, data=payload, format="json")
        payload = {
            "username": "usual_username",
            "password": "@G1tshahov",
        }

        response = self.client.post(self.url + 'login/', data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNot(response.json()["token"], None)

    def test_logout_company(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.05,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        self.client.post(self.url, data=payload, format="json")

        payload = {
            "username": "usual_username",
            "password": "@G1tshahov",
        }
        response = self.client.post(self.url + 'login/', data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNot(data["token"], None)
        self.assertEqual(self.client.get(self.url + data["company_id"] + '/',
                                         headers={"Authorization": "Bearer " + data['token']}).status_code,
                         status.HTTP_200_OK)

        response = self.client.post(self.url + 'logout/', headers={"Authorization": "Bearer " + data['token']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.url + data["company_id"] + '/',
                                         headers={"Authorization": "Bearer " + data['token']}).status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_get_company(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.05,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        response = self.client.post(self.url, data=payload, format="json")

        response = self.client.get(self.url + f'{response.json()["company_id"]}/',
                                   headers={"Authorization": "Bearer " + response.json()["token"]})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", data)
        self.assertEqual(data["name"], payload["name"])
        self.assertEqual(float(data["max_sale"]), payload["max_sale"])
        self.assertEqual(float(data["bonus_points_ratio"]), payload["bonus_points_ratio"])
        self.assertEqual(data["description"], payload["description"])
        self.assertEqual(data["username"], payload["username"])

    def test_update_company(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.05,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        response = self.client.post(self.url, data=payload, format="json")
        data = response.json()
        payload_update = {
            "name": "ООО Некофейня",
            "max_sale": 0.6,
            "bonus_points_ratio": 0.1,
            "description": "лучшее место для покупки велосипедов",
        }
        response = self.client.patch(self.url + data["company_id"] + '/',
                                     headers={"Authorization": "Bearer " + data["token"]}, data=payload_update,
                                     format="json")
        company = Company.objects.get(id=data["company_id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(company.name, payload_update["name"])
        self.assertEqual(float(company.max_sale), payload_update["max_sale"])
        self.assertEqual(float(company.bonus_points_ratio), payload_update["bonus_points_ratio"])
        self.assertEqual(company.description, payload_update["description"])

    def test_create_company_incorrect_data(self):
        payload = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": "fgsfg",
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_company_data_other_user(self):
        payload = [
            {
                "name": "ООО кофейня",
                "max_sale": 1,
                "bonus_points_ratio": 0.2,
                "description": "лучшее место для покупки кофе",
                "username": "usual_username",
                "password": "@G1tshahov"
            },
            {
                "name": "ООО Некофейня",
                "max_sale": 0.6,
                "bonus_points_ratio": 0.1,
                "description": "лучшее место для покупки велосипедов",
                "username": "huuu112",
                "password": "@G1tshahov"
            }
        ]

        data1 = self.client.post(self.url, data=payload[0], format="json").json()
        data2 = self.client.post(self.url, data=payload[1], format="json").json()

        payload_update = {
            "name": "ООО Некофейня",
            "max_sale": 0.6,
            "bonus_points_ratio": 0.1,
            "description": "лучшее место для покупки велосипедов",
        }

        response = self.client.patch(self.url + data2["company_id"] + '/',
                                     headers={"Authorization": "Bearer " + data1["token"]}, data=payload_update,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_company_data_other_user(self):
        payload = [
            {
                "name": "ООО кофейня",
                "max_sale": 1,
                "bonus_points_ratio": 0.2,
                "description": "лучшее место для покупки кофе",
                "username": "usual_username",
                "password": "@G1tshahov"
            },
            {
                "name": "ООО Некофейня",
                "max_sale": 0.6,
                "bonus_points_ratio": 0.1,
                "description": "лучшее место для покупки велосипедов",
                "username": "huuu112",
                "password": "@G1tshahov"
            }
        ]

        data1 = self.client.post(self.url, data=payload[0], format="json").json()
        data2 = self.client.post(self.url, data=payload[1], format="json").json()

        response = self.client.get(self.url + data2["company_id"] + '/',
                                     headers={"Authorization": "Bearer " + data1["token"]})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_fail_update = [
            {"name": "я"},
            {"name": "я" * 256},
            {"max_sale": 10},
            {"max_sale": -1},
            {"bonus_points_ratio": 10},
            {"bonus_points_ratio": -1},
            {"description": "я" * 1001},
            {"username": "s"},
            {"username": "s" * 256},
            {"password": "password"},
            {"password": "Pa!1"},
            {"password": "Pa!1" * 32},
        ]

        self.good_data = {
            "name": "ООО кофейня",
            "max_sale": 1,
            "bonus_points_ratio": 0.2,
            "description": "лучшее место для покупки кофе",
            "username": "usual_username",
            "password": "@G1tshahov"
        }

    def test_company_serializer(self):
        self.assertTrue(CompanySerializer(data=self.good_data).is_valid())
        for i in self.keys_for_fail_update:
            self.for_check = self.good_data | i
            self.assertFalse(CompanySerializer(data=self.for_check).is_valid(), msg=f"error in pair: {i}")
