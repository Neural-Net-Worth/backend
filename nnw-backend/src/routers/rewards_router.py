from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.redeemed_rewards import RedeemedRewards
from models.user_points import UserPoints
from models import SessionLocal
from pydantic import BaseModel
from datetime import datetime


class RedeemRewardRequest(BaseModel):
    reward_name: str
    # The actual gift card amount (the value of the reward)
    reward_amount: float
    needed_points: int


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}/redeemed-rewards")
def get_redeemed_rewards(user_id: int, db: Session = Depends(get_db)):
    redeemed_rewards = db.query(RedeemedRewards).filter(
        RedeemedRewards.user_id == user_id).all()
    if not redeemed_rewards:
        raise HTTPException(
            status_code=404, detail="No redeemed rewards found for this user")

    return [
        {
            "reward_name": reward.reward_name,
            "reward_amount": reward.reward_amount,
            "redeemed_at": reward.redeemed_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for reward in redeemed_rewards
    ]


@router.post("/{user_id}/redeemed-rewards")
def redeem_reward(user_id: int, request: RedeemRewardRequest, db: Session = Depends(get_db)):
    reward_name = request.reward_name
    reward_amount = request.reward_amount
    needed_points = request.needed_points

    # Check if the user has enough points
    user_points = db.query(UserPoints).filter(
        UserPoints.user_id == user_id).first()

    if not user_points or user_points.points < needed_points:
        raise HTTPException(
            status_code=400, detail="Not enough points to redeem this reward")

    # Set the redeemed_at field to the current time
    redeemed_at = datetime.now()

    # Create a new redeemed reward record
    new_reward = RedeemedRewards(
        user_id=user_id,
        reward_name=reward_name,
        reward_amount=reward_amount,
        needed_points=needed_points,
        redeemed_at=redeemed_at
    )

    # Add the new reward to the database
    db.add(new_reward)

    # Deduct the points
    user_points.points -= needed_points

    # Commit the changes to the database
    db.commit()

    return {"message": f"Reward '{reward_name}' redeemed successfully", "user_id": user_id, "reward_name": reward_name}
