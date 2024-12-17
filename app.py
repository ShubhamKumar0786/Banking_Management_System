from flask import Flask, render_template, request, redirect, flash
import pymysql.cursors
import random
import os
app = Flask(__name__)

# Secret key for flash messages
app.secret_key = os.urandom(24)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",  # Use localhost for the host
        user="root",  # Username for MySQL
        password="password",  # Password for MySQL
        database="bank_management",  # Replace with your actual database name
        port=3306,  # Default MySQL port
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form['username']
    account_number = str(random.randint(1000000000, 9999999999))
    contact_no = request.form['contact_no']
    amount = float(request.form['amount'])
    city = request.form['city']
    state = request.form['state']
    pin = request.form['pin']

    # Validation checks
    if amount >= 1000 and pin.isdigit() and len(pin) == 4:
        connection = get_db_connection()
        try:
            query = """
            INSERT INTO customers (account_number, username, contact_no, amount, city, state, pin) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (account_number, username, contact_no, amount, city, state, pin)
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                connection.commit()

            flash("Account created successfully!", "success")
            return render_template('dashboard.html', user={
                'account_number': account_number, 'username': username,
                'contact_no': contact_no, 'amount': amount, 'city': city, 'state': state
            })
        except Exception as e:
            flash(f"Error creating account: {e}", "danger")
            return render_template('index.html')
        finally:
            connection.close()
    else:
        flash("Invalid input or minimum amount not met.", "danger")
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    pin = request.form['pin']
    connection = get_db_connection()
    try:
        query = "SELECT * FROM customers WHERE username=%s AND pin=%s"
        with connection.cursor() as cursor:
            cursor.execute(query, (username, pin))
            result = cursor.fetchone()

        if result:
            return render_template('dashboard.html', user=result)
        else:
            flash("Account not found or incorrect PIN.", "danger")
            return render_template('index.html')
    except Exception as e:
        flash(f"Error during login: {e}", "danger")
        return render_template('index.html')
    finally:
        connection.close()

@app.route('/credit', methods=['POST'])
def credit():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])
    connection = get_db_connection()
    try:
        query = "UPDATE customers SET amount = amount + %s WHERE account_number=%s"
        with connection.cursor() as cursor:
            cursor.execute(query, (amount, account_number))
            connection.commit()

        flash("Amount credited successfully.", "success")
        return redirect('/')
    except Exception as e:
        flash(f"Error during credit: {e}", "danger")
        return redirect('/')
    finally:
        connection.close()

@app.route('/debit', methods=['POST'])
def debit():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])
    connection = get_db_connection()
    try:
        query = "SELECT amount FROM customers WHERE account_number=%s"
        with connection.cursor() as cursor:
            cursor.execute(query, (account_number,))
            balance = cursor.fetchone()

        if balance and amount <= balance['amount']:
            query = "UPDATE customers SET amount = amount - %s WHERE account_number=%s"
            with connection.cursor() as cursor:
                cursor.execute(query, (amount, account_number))
                connection.commit()

            flash("Amount debited successfully.", "success")
            return redirect('/')
        else:
            flash("Insufficient balance!", "danger")
            return redirect('/')
    except Exception as e:
        flash(f"Error during debit: {e}", "danger")
        return redirect('/')
    finally:
        connection.close()

@app.route('/delete', methods=['POST'])
def delete():
    account_number = request.form['account_number']
    connection = get_db_connection()
    try:
        query = "DELETE FROM customers WHERE account_number=%s"
        with connection.cursor() as cursor:
            cursor.execute(query, (account_number,))
            connection.commit()

        flash("Account deleted successfully.", "success")
        return redirect('/')
    except Exception as e:
        flash(f"Error during account deletion: {e}", "danger")
        return redirect('/')
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
