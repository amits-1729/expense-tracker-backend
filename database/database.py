import os
import mysql.connector
from mysql.connector import Error
from datetime import date


# class DBhelper:
#     def get_connection(self):
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="expense_tracker"
#         )
#         return conn
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
    
    # For registering using name, email, password
    def register(self, name, email, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}

        finally:
            cursor.close()
            conn.close()



    # fetching user's credentials using email
    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data
    

    # fetch user's creadentials using user_id
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data

    # add expense using user_id
    def add_expense(self, user_id, expense):
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
            cursor.close()
            conn.close()

    # fetch user's expenses using user_id
    def get_expenses(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC"
        cursor.execute(query, (user_id,))

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data
    
    # update expense using expense_id
    def update_expense(self, expense_id, user_id, expense):
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
            UPDATE expenses
            SET {", ".join(fields)}
            WHERE id=%s AND user_id=%s
            """

            values.extend([expense_id, user_id])

            cursor.execute(query, tuple(values))
            conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}

        finally:
            cursor.close()
            conn.close()

    #  delete expense using expense_id
    def delete_expense(self, expense_id, user_id):
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
            cursor.close()
            conn.close()


    # get categories default as well as user specific
    def get_categories(self,user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT name,id FROM categories WHERE user_id=%s OR is_default = TRUE"
            cursor.execute(query,(user_id,))

            data = cursor.fetchall()
        except Error as e:
            return {"error": str(e)}
        finally:
            cursor.close()
            conn.close()

        return data
    
    # add category using user_id
    def add_category(self,user_id,category):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            check_query = """SELECT 1 FROM categories WHERE name = %s AND (is_default = TRUE OR user_id = %s);"""
            values = (category,user_id)
            cursor.execute(check_query, values)
            result = cursor.fetchone()

            if result:
                return {"message": "Category already exist"}
            else:
                query = """INSERT INTO categories (name, user_id, is_default) VALUES (%s, %s, FALSE);"""
                cursor.execute(query,values)
                conn.commit()
                return {"message": "category added successfully"}

        except Error as e:
            return {"error": str(e)}

        finally:
            cursor.close()
            conn.close()

    # for deleting category using category id
    def del_category(self,cat_id,user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """DELETE FROM categories WHERE id = %s and user_id = %s"""
            cursor.execute(query,(cat_id,user_id))
            conn.commit()

            return {"message":"Category deleted succefully"}

        except Error as e:
            return {"error": str(e)}
        
        finally:
            cursor.close()
            conn.close()


    # def get_daily_trend(self, user_id):
    #     conn = self.get_connection()
    #     cursor = conn.cursor(dictionary=True)
    #     query = """
    #     SELECT DATE(expense_date) as day, SUM(amount) as total
    #     FROM expenses
    #     WHERE user_id = %s
    #     GROUP BY day
    #     ORDER BY day;
    #     """
    #     cursor.execute(query,(user_id,))
    #     data = cursor.fetchall()

    #     cursor.close()
    #     conn.close()

    #     return data
    

    def get_today_category_split(self, user_id):
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

        cursor.close()
        conn.close()

        return data

    def get_today_metrics(self, user_id):
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

        return data
    

    def get_yesterday_metrics(self, user_id):
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

        cursor.close()
        conn.close()

        return data