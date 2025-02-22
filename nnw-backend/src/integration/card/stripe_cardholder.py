from .cardholder import CardholderIssuer


class StripeCardholderIssuer(CardholderIssuer):
    def __init__(self, stripe_api_key: str):
        import stripe
        stripe.api_key = stripe_api_key
        self.stripe = stripe

    def create_cardholder(self, name: str, email: str, phone_number: str, address: str) -> dict:
        """
        Creates a cardholder using Stripe Issuing.
        For individuals, the type is "individual". Billing address is passed as part of the billing object.
        """
        cardholder = self.stripe.issuing.Cardholder.create(
            type="individual",
            name=name,
            email=email,
            phone_number=phone_number,
            billing={
                "address": {
                    "line1": address
                }
            }
        )
        return cardholder
