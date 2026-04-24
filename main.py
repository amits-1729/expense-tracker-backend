from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.database import DBhelper
from schemas.schemas import RegisterUser, LoginUser, CategoryCreate,AddExpense, UpdateExpense, CategoryDelete
from utils.password import hash_password, verify_password
from utils.jwt_handler import create_access_token, verify_token
from fastapi import Query


app = FastAPI()
security = HTTPBearer()
db = DBhelper()


# for home page
@app.get("/")
def home():
    return {"message":"Welcome to expense tracker app"}


# register api-----------------------------------------------------------------
@app.post("/register")
def register(user: RegisterUser):
    hashed_password = hash_password(user.password)
    response = db.register(user.name, user.email, hashed_password)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": "Registration successful"}
    

# login api ------------------------------------------------------------------
@app.post("/login")
def login(user: LoginUser):
    data = db.get_user_by_email(user.email)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": data["id"]})
    return {
        "access_token": token,
        "user_name": data["name"]
    }


# for checking authentication-----------------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.get_user_by_id(user_id) # is there any user with this id or not
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user_id

# Transaction APIs-----------------------------------------------------------
@app.post("/add-expense")
def add_expense(expense: AddExpense, current_user: int = Depends(get_current_user)):
    response = db.add_expense(current_user, expense)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": "Expense added successfully"}
    

@app.get("/get-expense")
def get_expenses(current_user: int = Depends(get_current_user)):
    response = db.get_expenses(current_user)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


@app.put("/update-expense/{expense_id}")
def update_expense(expense_id: int, expense: UpdateExpense, current_user: int = Depends(get_current_user)):
    response = db.update_expense(expense_id, expense)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": "Expense updated successfully"}
    

@app.delete("/delete-expense/{expense_id}")
def delete_expense(expense_id: int, current_user: int = Depends(get_current_user)):
    response = db.delete_expense(expense_id, current_user)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": "Expense deleted successfully"}
    

# Categories APIs---------------------------------------------------------------

@app.get("/get-categories")
def get_categories(current_user:int = Depends(get_current_user)):
    data = db.get_categories(current_user)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    return {
        "message": "categories fetched successfully",
        "categories": data
    }

@app.post("/add-category")
def add_category(user_input:CategoryCreate, current_user:int = Depends(get_current_user)):
    response = db.add_category(current_user,user_input.category)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {
        "message": response["message"]
    }

@app.delete("/delete-category")
def del_category(user_input:CategoryDelete, current_user:int = Depends(get_current_user)):
    response = db.del_category(user_input.id,current_user)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {
        "message": response["message"]
    }

@app.get("/expenses/daily-dashboard")
def daily_dashboard(current_user:int = Depends(get_current_user)):
    today_met = db.get_today_metric(current_user)
    yesterday = db.get_yesterday_metric(current_user)
    today_cat = db.get_daily_category_split(current_user)

    data = {
        "today_metric":today_met,
        "yesterday_metric": yesterday,
        "today_cat_split": today_cat
    }
    return data


@app.get("/expenses/weekly-dashboard")
def weekly_dashboard(current_user:int = Depends(get_current_user)):
    current_week_met = db.get_current_week_metrics(current_user)
    last_week_met = db.get_last_week_metrics(current_user)
    current_cat = db.get_weekly_category_split(current_user)
    daily_trend = db.get_daily_trend(current_user)

    data = {
        "current_week_metric":current_week_met,
        "last_week_metric": last_week_met,
        "current_week_cat_split": current_cat,
        "daily_trend":daily_trend
    }
    return data
