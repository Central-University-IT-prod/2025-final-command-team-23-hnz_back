import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from cashiers.serializers import CashierSerializer, CashierPreSaleSerializer, CashierSaleSerializer, \
    CashierItemSerializer


@pytest.mark.django_db
class CompanyTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.cashier_login_url = '/api/cashier/login/'
        self.cashier_logout_url = '/api/cashier/logout/'
        self.create_company_url = '/api/company/'
        self.cashier_pre_sale_url = '/api/cashier/pre-sale/'
        self.create_cashier_url = '/api/company/{company_id}/cashier/'
        self.create_client_url = '/api/client/register/'
        self.create_items_url = '/api/company/{company_id}/item/'
        self.cashier_sell_url = '/api/cashier/sell/'

    def init_data(self):
        payload = {
            "username": "test_company1",
            "name": "Test Company",
            "password": "Password1!"
        }
        response = self.client.post(self.create_company_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        company_id = data.get('company_id')
        company_token = data.get('token')

        payload = {
            "username": "test_cashier1",
            "password": "Password2!"
        }
        response = self.client.post(
            path=self.create_cashier_url.format(company_id=company_id),
            data=payload,
            headers={"Authorization": "Bearer " + company_token},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        cashier_id = data.get('cashier_id')
        cashier_token = data.get('token')

        payload_item = {
            "name": "Капучино",
            "price": 200
        }

        response = self.client.post(self.create_items_url.format(company_id=company_id), data=payload_item,
                                    headers={"Authorization": "Bearer " + company_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        item_id = data.get('id')

        return company_id, company_token, cashier_id, cashier_token, item_id

    def init_client(self):
        payload = {
            'id': 12344,
            'first_name': 'John',
        }
        response = self.client.post(self.create_client_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(str(data.get('id')), str(12344))
        self.assertEqual(data.get('first_name'), 'John')
        return data.get('id'), data.get('first_name')

    def test_cashier_login(self):
        company_id, company_token, cashier_id, cashier_token, item_id = self.init_data()

        payload = {
            "username": "test_cashier1",
            "password": "Password2!"
        }

        response = self.client.post(self.cashier_login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(str(company_id), str(data.get('company_id')))
        self.assertEqual(str(cashier_id), str(data.get('cashier_id')))

    def test_cashier_logout(self):
        company_id, company_token, cashier_id, cashier_token, item_id = self.init_data()

        payload = {
            "username": "test_cashier1",
            "password": "Password2!"
        }
        response = self.client.post(self.cashier_login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(str(company_id), str(data.get('company_id')))
        self.assertEqual(str(cashier_id), str(data.get('cashier_id')))

        response = self.client.post(
            path=self.cashier_logout_url,
            headers={"Authorization": "Bearer " + cashier_token},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            path=self.cashier_logout_url,
            data=payload,
            headers={"Authorization": "Bearer " + cashier_token},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cashier_pre_sale(self):
        company_id, company_token, cashier_id, cashier_token, item_id = self.init_data()
        client_id, client_first_name = self.init_client()

        payload = {
            'client_id': client_id,
            'total_price': 100
        }
        response = self.client.post(
            path=self.cashier_pre_sale_url,
            data=payload,
            headers={"Authorization": "Bearer " + cashier_token},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cashier_sell(self):
        company_id, company_token, cashier_id, cashier_token, item_id = self.init_data()
        client_id, client_first_name = self.init_client()
        payload = {
            'client_id': client_id,
            'total_price': 400
        }
        response = self.client.post(
            path=self.cashier_pre_sale_url,
            data=payload,
            headers={"Authorization": "Bearer " + cashier_token},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = {
            "items": [{"item_id": item_id, "quantity": 2, "sell_price": "400"}],
            "total_price_with_sale": 400,
            "total_price": 400,
            "points_used": 0,
            "client_id": client_id
        }
        response = self.client.post(
            path=self.cashier_sell_url,
            data=payload,
            headers={"Authorization": "Bearer " + cashier_token},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.content)


class CashierSerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_fail_update = [
            {"username": "u" * 256},
            {"password": "password"},
            {"password": "Pa$1"},
            {"password": "Pa$2" * 32},
        ]

        self.good_data = {
            "username": "username",
            "password": "@G1tshahov",
        }

    def test_company_serializer(self):
        self.assertTrue(CashierSerializer(data=self.good_data).is_valid())
        for i in self.keys_for_fail_update:
            self.for_check = self.good_data | i
            self.assertFalse(CashierSerializer(data=self.for_check).is_valid(), msg=f"error: {i}")


class CashierPreSaleSerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_fail_update = [
            {"client_id": "dfasdf"},
            {"total_price": "dfasdf"},
            {"total_price": 1231231231123},
        ]

        self.good_data = {
            "client_id": 12312,
            "total_price": 123.12,
        }

    def test_pre_sale_serializer(self):
        self.assertTrue(CashierPreSaleSerializer(data=self.good_data).is_valid())
        for i in self.keys_for_fail_update:
            self.for_check = self.good_data | i
            self.assertFalse(CashierPreSaleSerializer(data=self.for_check).is_valid(), msg=f"error: {i}")


class CashierSaleSerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_fail_update = [
            {"total_price_with_sale": 1312312321321},
            {"total_price": 1212.1231231}
        ]
        self.good_data = {
            "items": [{"item_id": "8ba88293-8535-4225-b457-e7fc4954ba6c", "quantity": 1, "sell_price": 12.12}],
            "total_price_with_sale": 123.12,
            "total_price": 123.12,
            "points_used": 123,
            "client_id": 123,
        }

    def test_sale_serializer(self):
        self.assertTrue(CashierSaleSerializer(data=self.good_data).is_valid())
        for i in self.keys_for_fail_update:
            self.for_check = self.good_data | i
            self.assertFalse(CashierSaleSerializer(data=self.for_check).is_valid(), msg=f"error: {i}")


class CashierItemSerializerTests(APITestCase):
    def setUp(self):
        self.keys_for_fail_update = [
            {"sell_price": 12.122},
            {"sell_price": 123333333333.22},
        ]

        self.good_data = {
            "item_id": "8ba88293-8535-4225-b457-e7fc4954ba6c",
            "quantity": 1,
            "sell_price": 12.12
        }

    def test_cashier_item_serializer(self):
        self.assertTrue(CashierItemSerializer(data=self.good_data).is_valid())
        for i in self.keys_for_fail_update:
            self.for_check = self.good_data | i
            self.assertFalse(CashierItemSerializer(data=self.for_check).is_valid(), msg=f"error: {i}")
