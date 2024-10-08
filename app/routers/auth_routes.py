from datetime import timedelta
from fastapi import APIRouter,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import quiz, schemas
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app import users, auth
from fastapi import Depends, HTTPException
from .. import models
from app.utils import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


# User registration route
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(db, email=user.email)
    user_name=users.get_user_by_username(db, username=user.username)
    if db_user or user_name:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    return users.create_user(db=db, user=user)



@router.post("/login")
def login_for_access_token(form_data: schemas.Loginschema, db: Session = Depends(get_db)):
    user = users.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username,"user_id": user.id,"role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "role": user.role}

# Get current user
@router.get("/users/me/streak", response_model=schemas.Streak)
def get_user_streak(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return quiz.get_user_streak(db=db, user=current_user)