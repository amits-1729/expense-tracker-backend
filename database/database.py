import os
import mysql.connector
from mysql.connector import Error


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
    def get_connection(self):
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return conn
    # REGISTER
    def register(self, name, email, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            conn.commit()
            return {"success": True}

        except Error as e:
            return {"error": str(e)}

        finally:
            cursor.close()
            conn.close()



    # GET USER BY EMAIL
    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data
    

    # GET USER BY USER ID
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data

    # ADD EXPENSE (FIXED: user_id)
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

    # GET EXPENSES
    def get_expenses(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC"
        cursor.execute(query, (user_id,))

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data
    
    # UPDATE EXPENSE
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

    #  DELETE
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


    # GET CATEGORIES
    def get_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM categories"
        cursor.execute(query)

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data

    def get_daily_trend(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT DATE(expense_date) as day, SUM(amount) as total
        FROM expenses
        WHERE user_id = %s
        GROUP BY day
        ORDER BY day;
        """
        cursor.execute(query,(user_id,))
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data
    

