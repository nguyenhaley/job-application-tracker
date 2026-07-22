from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate, UserOut
from auth import hash_password
from auth import hash_password, verify_password, create_access_token
from schemas import UserLogin
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)): 
    # hash user password using hash_password()
    hashed_password = hash_password(user.password)
    # create new_user object with email and hashed password
    new_user = User(email=user.email, password_hash=hashed_password)

    # add new_user to session, commit, and refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # look up user by their email
    current_user = db.query(User).filter(User.email == credentials.email).first()
    
    # if user not found in database, return 401 error
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # check if password matches using verify_password()
    check_password = verify_password(credentials.password, current_user.password_hash)
    # raise 401 error if password doesn't match
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # create access token and return it since passwords match and user was found
    else:
        token = create_access_token({"sub": str(current_user.id)})
        return {"access_token": token, "token_type": "bearer"}
    
@app.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user