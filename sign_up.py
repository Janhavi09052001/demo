import streamlit as st
import pymssql
import re  # For regular expression validation
from datetime import datetime

# Function to connect to the Azure SQL Database using pymssql
def connect_to_db():
    # Replace with your Azure SQL Database connection details
    conn = pymssql.connect(
        server='demo-trial.database.windows.net',  # Replace with your server name
        user='server',                            # Replace with your username
        password='abcd123@',                      # Replace with your password
        database='demo-trial'                     # Replace with your database name
    )
    return conn

# Function to check if the user_name already exists in the database
def check_user_name_exists(user_name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # SQL query to check if the user_name already exists
        cursor.execute("SELECT COUNT(1) FROM ev_user_data WHERE user_name = %s", (user_name,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        # If the user_name exists, return True, otherwise False
        return result[0] > 0
    except Exception as e:
        st.error(f"Error checking user_name in the database: {e}")
        return False

# Function to insert user data into the database
def insert_user_data(first_name, last_name, user_name, password):
    try:
        # Connect to the database
        conn = connect_to_db()
        cursor = conn.cursor()

        # SQL query to insert data into ev_user_data table
        cursor.execute("""
            INSERT INTO ev_user_data (first_name, last_name, user_name, password)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, user_name, password))

        # Commit the transaction
        conn.commit()
        cursor.close()
        conn.close()

        st.success("Sign Up Successful!")
        st.write(f"User Name: {user_name}")
    except Exception as e:
        st.error(f"Error inserting data into the database: {e}")

# Function to validate the email based on the rules
def validate_email(email):
    # Regex pattern for email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Check if the email matches the pattern
    if not re.match(email_pattern, email):
        return "Invalid email format. Make sure it follows the format: username@domain.tld."

    # Additional validation rules
    local_part, domain_part = email.split('@')

    # Check local part length
    if not (1 <= len(local_part) <= 64):
        return "The local part (username) of the email must be between 1 and 64 characters."

    # Check domain part length
    if not (1 <= len(domain_part) <= 253):
        return "The domain part of the email must be between 1 and 253 characters."

    # Check for consecutive dots in the local part
    if '..' in local_part:
        return "The local part (username) cannot contain consecutive dots."

    # Check for leading or trailing dots in the local part or domain part
    if local_part.startswith('.') or local_part.endswith('.'):
        return "The local part (username) cannot start or end with a dot."
    if domain_part.startswith('.') or domain_part.endswith('.'):
        return "The domain part cannot start or end with a dot."

    # Check that there is at least one dot in the domain part and TLD is valid
    if '.' not in domain_part:
        return "The domain part must contain at least one dot."
    
    # Check the TLD length (must be at least 2 characters)
    tld = domain_part.split('.')[-1]
    if len(tld) < 2:
        return "The top-level domain (TLD) must be at least 2 characters long."

    return None  # Email is valid

# Function to validate password based on rules
def validate_password(password):
    # Password validation rules using regex
    # Password must contain at least:
    # 1 uppercase letter, 1 lowercase letter, 1 special character, and be at least 8 characters long
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\W).{8,}$'
    
    if not re.match(password_pattern, password):
        return "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one special character."
    
    return None  # Password is valid

# Set up the title of the app
st.title("Sign Up Page")

# Create the form for user signup
with st.form(key='signup_form'):
    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    user_name = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    confirm_password = st.text_input("Confirm Password", type='password')

    # Submit button
    submit_button = st.form_submit_button("Sign Up")

# Handle form submission
if submit_button:
    # Check if passwords match
    if password != confirm_password:
        st.error("Passwords do not match!")
    elif first_name and last_name and user_name and password:
        # Validate the email
        email_validation_error = validate_email(user_name)  # Treating user_name as email for validation
        if email_validation_error:
            st.error(email_validation_error)  # Show email validation error
        else:
            # Validate the password
            password_validation_error = validate_password(password)
            if password_validation_error:
                st.error(password_validation_error)  # Show password validation error
            else:
                # Check if user_name already exists in the database
                if check_user_name_exists(user_name):
                    st.error("This user name already exists. Please use another one.")
                else:
                    # Insert data into the database
                    insert_user_data(first_name, last_name, user_name, password)
    else:
        st.error("Please fill in all fields.")
