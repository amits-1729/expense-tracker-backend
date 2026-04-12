from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.database import DBhelper
from schemas.user_schema import RegisterUser, LoginUser
from utils.password import hash_password, verify_password
from utils.jwt_handler import create_access_token, verify_token
from schemas.expense_schema import AddExpense, UpdateExpense
from fastapi import Query



app = FastAPI()
security = HTTPBearer()

db = DBhelper()

# register api
@app.post("/register")
def register(user: RegisterUser):
    hashed_password = hash_password(user.password)
    response = db.register(user.name, user.email, hashed_password)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": "Registration successful"}
    
# login api that give access_token and username
@app.post("/login")
def login(user: LoginUser):
    data = db.get_user_by_email(user.email)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": data["id"]})
    return {
        "access_token": token,
        "user_name": data["name"]
    }



def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # before return user_id first check is any user exist with this id
    user = db.get_user_by_id(user_id) 
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user_id


# @app.get("/profile")
# def profile(current_user: str = Depends(get_current_user)):
#     return { 
#         "message": "Welcome to your profile",
#         "user_email": current_user
#     }

@app.post("/add-expense")
def add_expense(expense: AddExpense, current_user: int = Depends(get_current_user)):
    response = db.add_expense(current_user, expense)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return {"message": "Expense added successfully"}
    

@app.get("/expenses")
def get_expenses(current_user: int = Depends(get_current_user)):
    data = db.get_expenses(current_user)
    return {"expenses": data}


@app.put("/update-expense/{expense_id}")
def update_expense(expense_id: int, expense: UpdateExpense, current_user: int = Depends(get_current_user)):
    response = db.update_expense(expense_id, current_user, expense)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return {"message": "Expense updated successfully"}
    

@app.delete("/delete-expense/{expense_id}")
def delete_expense(expense_id: int, current_user: int = Depends(get_current_user)):
    response = db.delete_expense(expense_id, current_user)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return {"message": "Expense deleted successfully"}
    
@app.get("/categories")
def get_categories():
    data = db.get_categories()
    return {"categories": data}


@app.get("/expenses/trend")
def get_expense_trend(type: str = Query(...), current_user: int = Depends(get_current_user)):

    if type != "daily":
        raise HTTPException(status_code=400, detail="For now only daily supported")

    data = db.get_daily_trend(current_user)

    return data