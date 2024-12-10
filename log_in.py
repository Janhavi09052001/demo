import streamlit as st
import pymssql
import re  # For regular expression validation
from datetime import datetime

# Function to connect to the Azure SQL Database using pymssql
def connect_to_db():
    # Replace with your Azure SQL Database connection details
    conn = pymssql.connect(
        server='demo-trial.database.windows.net',  # Replace with your server name
        user='server',                         # Replace with your username
        password='abcd123@',                   # Replace with your password
        database='demo-trial'                    # Replace with your database name
    )
    return conn

# Function to check if the user_name and password are correct (for login)
def check_user_credentials(user_name, password):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # SQL query to check if the user_name and password match
        cursor.execute("SELECT COUNT(1) FROM ev_user_data WHERE user_name = %s AND password = %s", (user_name, password))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        # If the credentials match, return True, otherwise False
        return result[0] > 0
    except Exception as e:
        st.error(f"Error checking user credentials: {e}")
        return False

# Function to validate the user_name based on the rules (used for login)
def validate_user_name(user_name):
    # Regex pattern for user_name validation (similar to email validation)
    user_name_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Check if the user_name matches the pattern
    if not re.match(user_name_pattern, user_name):
        return "Invalid user_name format. Make sure it follows the format: username@domain.tld."

    # Additional validation rules
    local_part, domain_part = user_name.split('@')

    # Check local part length
    if not (1 <= len(local_part) <= 64):
        return "The local part (username) of the user_name must be between 1 and 64 characters."

    # Check domain part length
    if not (1 <= len(domain_part) <= 253):
        return "The domain part of the user_name must be between 1 and 253 characters."

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

    return None  # user_name is valid

# Function to validate password based on rules (used for login)
def validate_password(password):
    # Password validation rules using regex
    # Password must contain at least:
    # 1 uppercase letter, 1 lowercase letter, 1 special character, and be at least 8 characters long
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\W).{8,}$'
    
    if not re.match(password_pattern, password):
        return "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one special character."
    
    return None  # Password is valid

# Set up the title of the app
st.title("Login Page")

# Create the form for user login
with st.form(key='login_form'):
    user_name = st.text_input("User Name")
    password = st.text_input("Password", type='password')

    # Submit button
    submit_button = st.form_submit_button("Login")

# Handle form submission for Login
if submit_button:
    if user_name and password:
        # Validate the user_name format
        user_name_validation_error = validate_user_name(user_name)
        if user_name_validation_error:
            st.error(user_name_validation_error)  # Show user_name validation error
        else:
            # Validate the password format
            password_validation_error = validate_password(password)
            if password_validation_error:
                st.error(password_validation_error)  # Show password validation error
            else:
                # Check if the credentials are correct (user_name + password)
                if check_user_credentials(user_name, password):
                    st.success("Login Successful!")
                    st.write(f"Welcome back, {user_name}!")
                else:
                    st.error("Invalid user name or password. Please try again.")
    else:
        st.error("Please fill in both user name and password.")
