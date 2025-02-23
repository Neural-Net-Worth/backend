import uuid
from .cardholder import CardholderIssuer


class MockCardholderIssuer(CardholderIssuer):
    def create_cardholder(self, name: str, email: str, phone_number: str, address: str) -> dict:
        """
        Mock implementation of the CardholderIssuer interface.
        Generates a mock cardholder ID and returns test data.
        """
        cardholder_id = f"mock_cardholder_{uuid.uuid4().hex[:8]}"
        return {
            "id": cardholder_id,
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "address": address,
            "provider": "mock"
        }
