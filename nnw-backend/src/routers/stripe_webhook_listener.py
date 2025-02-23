import stripe
from fastapi import APIRouter, Request, HTTPException
from config import settings

router = APIRouter()

stripe.api_key = settings.STRIPE_API_KEY
# Your webhook secret from Stripe
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Verify the webhook signature to ensure the request is from Stripe.
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process the event. For a one-time card, we assume an authorization event indicates usage.
    if event["type"] == "issuing.authorization.created":
        auth = event["data"]["object"]
        # Extract the card id from the authorization object.
        card_id = auth.get("card", {}).get("id")
        if card_id:
            try:
                # Cancel the card to prevent further use.
                stripe.issuing.Card.update(card_id, status="canceled")
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    # Acknowledge receipt of the event.
    return {"status": "success"}
