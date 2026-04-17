from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.database import DBhelper
from schemas.user_schema import RegisterUser, LoginUser, CategoryCreate
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
    
    if not verify_password(user.password, data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": data["id"]})
    return {
        "access_token": token,
        "user_name": data["name"]
    }


# for checking authentication
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
def del_category(user_input:CategoryCreate, current_user:int = Depends(get_current_user)):
    response = db.del_category(user_input.id,current_user)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {
        "message": response["message"]
    }


@app.get("/expenses/category-split")
def get_category_split(
    filter: str = Query("today"), 
    current_user: int = Depends(get_current_user)
):
    
    if filter == "today":
        data = db.get_today_category_split(current_user)

    elif filter == "month":
        data = db.get_category_split_month(current_user)

    else:
        raise HTTPException(status_code=400, detail="Invalid filter")

    return {
        "cat_expenses": data
    }

@app.get("/expenses/daily-metrics")
def daily_metrics(
    filter: str = Query("today"),
    current_user: int = Depends(get_current_user)
):
    if filter == "today":
        data = db.get_today_metrics(current_user)
    elif filter == "yesterday":
        data = db.get_yesterday_metrics(current_user)
    else:
        raise HTTPException(status_code=400, detail="Invalid filter")
    return data