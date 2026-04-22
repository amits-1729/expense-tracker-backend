import os
import mysql.connector
from mysql.connector import Error
from datetime import date

from dotenv import load_dotenv
load_dotenv()


class DBhelper:
    
    # For connecting to database
 
    def get_connection(self):
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return conn


    # Register function
    def register(self, name, email, password):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()

            return {"success": True}

        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    # Fetch user's credentials-------------------------------------------------

    # Fetch user's credentials by email
    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data
    

    # Fetch user's creadentials by user_id
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()
        return data


    # Transaction Operation by user_id-----------------------------------------

    # ADD Expenses
    def add_expense(self, user_id, expense):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

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

            cursor.execute(query, values)
            conn.commit()

            return {"success": True}

        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # GET Expenses
    def get_expenses(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC"
            cursor.execute(query, (user_id,))
            data = cursor.fetchall()
            return {"expenses":data}
        
        except Error as e:
            return {"error": str(e)}
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # EDIT Expenses by expense_id ----------------------------------------------------
    def update_expense(self, expense_id, expense):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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

            cursor.execute(query, tuple(values))
            conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    #  DELETE expense by expense_id --------------------------------------------------
    def delete_expense(self, expense_id, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM expenses WHERE id=%s AND user_id=%s"
            cursor.execute(query, (expense_id, user_id))
            conn.commit()
            return {"success": True}
        
        except Error as e:
            return {"error": str(e)}
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    # CRUD Operations in category by user_id ---------------------------------------------------
    # GET Categories
    def get_categories(self,user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT name,id FROM categories WHERE user_id=%s OR is_default = TRUE"
            cursor.execute(query,(user_id,))
            data = cursor.fetchall()
            return data

        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # ADD Category 
    def add_category(self,user_id,category):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            check_query = """SELECT 1 FROM categories WHERE name = %s AND (is_default = TRUE OR user_id = %s);"""
            values = (category,user_id)
            cursor.execute(check_query, values)
            result = cursor.fetchone()

            if result:
                return {"message": "Category already exist"}
            else:
                query = """
                    INSERT INTO categories (name, user_id, is_default) VALUES (%s, %s, FALSE);
                """
                cursor.execute(query,values)
                conn.commit()
                return {"message": "category added successfully"}

        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # DELETE Category 
    def del_category(self,cat_id,user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """DELETE FROM categories WHERE id = %s and user_id = %s"""
            cursor.execute(query,(cat_id,user_id))
            conn.commit()
            return {"message":"Category deleted succefully"}

        except Error as e:
            return {"error": str(e)}
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

   

    def get_today_metric(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
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
            cursor.execute(query, (user_id,))
            data = cursor.fetchone()

            if data["total_spend"] is None:
                data["total_spend"] = 0

            if data["avg_spend"] is None:
                data["avg_spend"] = 0

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

    def get_yesterday_metric(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT 
                SUM(amount) as total_spend,
                COUNT(*) as total_transactions,
                AVG(amount) as avg_spend
                FROM expenses
                WHERE user_id = %s
                AND DATE(expense_date) = CURDATE() - INTERVAL 1 DAY;
            """

            cursor.execute(query, (user_id,))
            data = cursor.fetchone()

            # Handle NULL values
            if data["total_spend"] is None:
                data["total_spend"] = 0

            if data["avg_spend"] is None:
                data["avg_spend"] = 0

            return data

        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_daily_category_split(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.name as category, SUM(e.amount) as total
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s 
                AND DATE(e.expense_date) = CURDATE()
                GROUP BY c.name;
            """
            cursor.execute(query, (user_id,))
            data = cursor.fetchall()

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

    def get_current_week_metrics(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
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
            cursor.execute(query, (user_id,))
            data = cursor.fetchone()

            if data["total_spend"] is None:
                data["total_spend"] = 0

            if data["avg_spend"] is None:
                data["avg_spend"] = 0

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_last_week_metrics(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
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
            cursor.execute(query, (user_id,))
            data = cursor.fetchone()

            if data["total_spend"] is None:
                data["total_spend"] = 0

            if data["avg_spend"] is None:
                data["avg_spend"] = 0

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

    def get_weekly_category_split(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.name as category, SUM(e.amount) as total
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s 
                AND expense_date >= CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY
                AND expense_date <= CURDATE()
                GROUP BY c.name;
            """

            cursor.execute(query, (user_id,))
            data = cursor.fetchall()

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    

    def get_daily_trend(self, user_id):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT expense_date AS date, SUM(amount) AS total_spent
                FROM expenses
                WHERE user_id = %s
                AND expense_date >= CURDATE() - INTERVAL 6 DAY
                AND expense_date <= CURDATE() 
                GROUP BY date
            """
            cursor.execute(query,(user_id,))
            data = cursor.fetchall()

            return data
        
        except Error as e:
            return {"error": str(e)}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()