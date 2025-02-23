from abc import ABC, abstractmethod


class CardholderIssuer(ABC):
    @abstractmethod
    def create_cardholder(self, name: str, email: str, phone_number: str, address: str) -> dict:
        """
        Create a cardholder in the card issuing system.

        Parameters:
          - name: Full name of the cardholder.
          - email: Email address.
          - phone_number: Contact phone number.
          - address: Billing address (as a string or serialized structure).

        Returns:
          A dictionary containing cardholder details (including a unique cardholder id).

        Raises:
          An exception if cardholder creation fails.
        """
        pass
