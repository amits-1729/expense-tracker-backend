import os
import mysql.connector
from mysql.connector import Error
import sys
from datetime import date

from dotenv import load_dotenv
load_dotenv()


class DBhelper:
    
    # For connecting to database
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=int(os.getenv("DB_PORT", 3306))
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except:
            sys.exit(0)


    # Register function
    def register(self, name, email, password):
        try:
            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (name, email, password))
            self.conn.commit()
            return {"success": True}
        except Error as e:
            return {"error": str(e)}


    # Fetch user's credentials-------------------------------------------------

    # Fetch user's credentials by email
    def get_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(query, (email,))
        data = self.cursor.fetchone()
        return data
    

    # Fetch user's creadentials by user_id
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchone()
        return data


    # Transaction Operation by user_id-----------------------------------------

    # ADD Expenses
    def add_expense(self, user_id, expense):
        try:
            query = """
            INSERT INTO expenses (user_id, category_id, amount, description, expense_date, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                user_id,
                expense.category_id,
                expense.amount,
                expense.description,
                expense.expense_date,
                expense.payment_method
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}

    # GET Expenses
    def get_expenses(self, user_id):
        try:
            query = "SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC"
            self.cursor.execute(query, (user_id,))
            data = self.cursor.fetchall()
            return {"expenses":data}
        
        except Error as e:
            return {"error": str(e)}
    
    # EDIT Expenses by expense_id ----------------------------------------------------
    def update_expense(self, expense_id, expense):
        try:
            fields = []
            values = []

            if expense.category_id is not None:
                fields.append("category_id=%s")
                values.append(expense.category_id)

            if expense.amount is not None:
                fields.append("amount=%s")
                values.append(expense.amount)

            if expense.description is not None:
                fields.append("description=%s")
                values.append(expense.description)

            if expense.expense_date is not None:
                fields.append("expense_date=%s")
                values.append(expense.expense_date)

            if expense.payment_method is not None:
                fields.append("payment_method=%s")
                values.append(expense.payment_method)

            if not fields:
                return {"error": "No fields to update"}

            query = f""" 
                UPDATE expenses SET {", ".join(fields)}WHERE id=%s
            """
            values.extend([expense_id])

            self.cursor.execute(query, tuple(values))
            self.conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}


    #  DELETE expense by expense_id --------------------------------------------------
    def delete_expense(self, expense_id, user_id):
        try:
            query = "DELETE FROM expenses WHERE id=%s AND user_id=%s"
            self.cursor.execute(query, (expense_id, user_id))
            self.conn.commit()
            return {"success": True}
        
        except Error as e:
            return {"error": str(e)}


    # CRUD Operations in category by user_id ---------------------------------------------------
    # GET Categories
    def get_categories(self,user_id):
        try:
            query = "SELECT name,id FROM categories WHERE user_id=%s OR is_default = TRUE"
            self.cursor.execute(query,(user_id,))
            data = self.cursor.fetchall()

        except Error as e:
            return {"error": str(e)}

        return data
    
    # ADD Category 
    def add_category(self,user_id,category):
        try:
            check_query = """SELECT 1 FROM categories WHERE name = %s AND (is_default = TRUE OR user_id = %s);"""
            values = (category,user_id)
            self.cursor.execute(check_query, values)
            result = self.cursor.fetchone()

            if result:
                return {"message": "Category already exist"}
            else:
                query = """
                    INSERT INTO categories (name, user_id, is_default) VALUES (%s, %s, FALSE);
                """
                self.cursor.execute(query,values)
                self.conn.commit()
                return {"message": "category added successfully"}

        except Error as e:
            return {"error": str(e)}

    # DELETE Category 
    def del_category(self,cat_id,user_id):
        try:
            query = """DELETE FROM categories WHERE id = %s and user_id = %s"""
            self.cursor.execute(query,(cat_id,user_id))
            self.conn.commit()
            return {"message":"Category deleted succefully"}

        except Error as e:
            return {"error": str(e)}
    

   

    def get_today_metric(self, user_id):
        query = """
            SELECT 
            SUM(amount) as total_spend,
            COUNT(*) as total_transactions,
            AVG(amount) as avg_spend
            FROM expenses
            WHERE user_id = %s
            AND expense_date >= CURDATE()
            AND expense_date < CURDATE() + INTERVAL 1 DAY;
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchone()

        if data["total_spend"] is None:
            data["total_spend"] = 0

        if data["avg_spend"] is None:
            data["avg_spend"] = 0

        return data
    

    def get_yesterday_metric(self, user_id):
        query = """
            SELECT 
            SUM(amount) as total_spend,
            COUNT(*) as total_transactions,
            AVG(amount) as avg_spend
            FROM expenses
            WHERE user_id = %s
            AND DATE(expense_date) = CURDATE() - INTERVAL 1 DAY;
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchone()

        if data["total_spend"] is None:
            data["total_spend"] = 0

        if data["avg_spend"] is None:
            data["avg_spend"] = 0

        return data
    
    def get_daily_category_split(self, user_id):
        query = """
            SELECT c.name as category, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s 
            AND DATE(e.expense_date) = CURDATE()
            GROUP BY c.name;
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchall()

        return data
    

    def get_current_week_metrics(self, user_id):
        query = """
            SELECT 
            SUM(amount) as total_spend,
            COUNT(*) as total_transactions,
            AVG(amount) as avg_spend
            FROM expenses
            WHERE user_id = %s
            AND expense_date >= CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY
            AND expense_date <= CURDATE();
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchone()

        if data["total_spend"] is None:
            data["total_spend"] = 0

        if data["avg_spend"] is None:
            data["avg_spend"] = 0

        return data
    
    def get_last_week_metrics(self, user_id):
        query = """
            SELECT 
            SUM(amount) as total_spend,
            COUNT(*) as total_transactions,
            AVG(amount) as avg_spend
            FROM expenses
            WHERE user_id = %s
            AND expense_date >= CURDATE() - INTERVAL (WEEKDAY(CURDATE()) + 7) DAY
            AND expense_date < CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY;
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchone()

        if data["total_spend"] is None:
            data["total_spend"] = 0

        if data["avg_spend"] is None:
            data["avg_spend"] = 0

        return data
    

    def get_weekly_category_split(self, user_id):
        query = """
            SELECT c.name as category, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s 
            AND expense_date >= CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY
            AND expense_date <= CURDATE()
            GROUP BY c.name;
        """

        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchall()

        return data
    

    def get_daily_trend(self, user_id):
        query = """
            SELECT expense_date AS date, SUM(amount) AS total_spent
            FROM expenses
            WHERE user_id = %s
            AND expense_date >= CURDATE() - INTERVAL 6 DAY
            AND expense_date <= CURDATE() 
            GROUP BY date
        """
        self.cursor.execute(query,(user_id,))
        data = self.cursor.fetchall()

        return data