from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class LoyalTBackendAuth(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_type = request.data.get('user_type')

        if not user_type:
            return None

        if user_type == User.UserTypeChoices.Cashier:
            try:
                cashier = User.objects.get(cashier__username=username)
                if cashier.check_password(password):
                    return cashier
            except ObjectDoesNotExist:
                return None
        if user_type == User.UserTypeChoices.Company:
            try:
                company = User.objects.get(company__username=username)
                if company.check_password(password):
                    return company
            except ObjectDoesNotExist:
                return None
        return None