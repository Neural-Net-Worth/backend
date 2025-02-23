# user_points_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user_points import UserPoints
from models import SessionLocal
from pydantic import BaseModel
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AddPointsRequest(BaseModel):
    points_to_add: float


@router.get("/{user_id}/points")
def get_user_points(user_id: int, db: Session = Depends(get_db)):
    if user_id:
        user_points = db.query(UserPoints).filter(
            UserPoints.user_id == user_id).first()
        print(user_points)
        if not user_points:
            raise HTTPException(
                status_code=404, detail="User points not found")
        return {"user_id": user_points.user_id, "points": user_points.points}


@router.post("/{user_id}/add-points")
def add_points(user_id: int, request: AddPointsRequest, db: Session = Depends(get_db)):
    points_to_add = request.points_to_add
    user_points = db.query(UserPoints).filter(
        UserPoints.user_id == user_id).first()
    if not user_points:
        user_points = UserPoints(user_id=user_id, points=0)
        db.add(user_points)
    user_points.points += points_to_add
    db.commit()
    return {"message": f"{points_to_add} points added to user {user_id}", "user_id": user_id, "new_points": user_points.points}
