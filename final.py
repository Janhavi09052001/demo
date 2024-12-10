import streamlit as st
import pymssql
import re  # For regular expression validation

# Function to connect to the Azure SQL Database using pymssql
def connect_to_db():
    conn = pymssql.connect(
        server='demo-trial.database.windows.net',  # Replace with your server name
        user='server',                            # Replace with your username
        password='abcd123@',                      # Replace with your password
        database='demo-trial'                     # Replace with your database name
    )
    return conn

# Function to check if the user_name and password are correct (for login)
def check_user_credentials(user_name, password):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(1) FROM ev_user_data WHERE user_name = %s AND password = %s", (user_name, password))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result[0] > 0
    except Exception as e:
        st.error(f"Error checking user credentials: {e}")
        return False

# Function to validate the user_name based on the rules (used for login)
def validate_user_name(user_name):
    user_name_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(user_name_pattern, user_name):
        return "Invalid user_name format. Make sure it follows the format: username@domain.tld."

    local_part, domain_part = user_name.split('@')

    if not (1 <= len(local_part) <= 64):
        return "The local part (username) of the user_name must be between 1 and 64 characters."

    if not (1 <= len(domain_part) <= 253):
        return "The domain part of the user_name must be between 1 and 253 characters."

    if '..' in local_part:
        return "The local part (username) cannot contain consecutive dots."

    if local_part.startswith('.') or local_part.endswith('.'):
        return "The local part (username) cannot start or end with a dot."
    if domain_part.startswith('.') or domain_part.endswith('.'):
        return "The domain part cannot start or end with a dot."

    if '.' not in domain_part:
        return "The domain part must contain at least one dot."
    
    tld = domain_part.split('.')[-1]
    if len(tld) < 2:
        return "The top-level domain (TLD) must be at least 2 characters long."

    return None  # user_name is valid

# Function to validate password based on rules (used for login and reset)
def validate_password(password):
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\W).{8,}$'
    
    if not re.match(password_pattern, password):
        return "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one special character."
    
    return None  # Password is valid

# Read and inject CSS into the app from an external file
with open("styles.css") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Set up the title of the app
st.title("Loginn ")

# Create the form for user login inside a styled container
with st.form(key='login_form', clear_on_submit=True):
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    user_name = st.text_input("User Name", key="username")
    password = st.text_input("Password", type='password', key="password")

    submit_button = st.form_submit_button( label="Login")
    st.markdown('</div>', unsafe_allow_html=True)

# Handle Forgot Password Button
if st.button("Forgot Password?"):
    with st.form(key='forgot_password_form'):
        email = st.text_input("Enter your registered email (user_name):")
        submit_forgot_button = st.form_submit_button("Request Password Reset")

    if submit_forgot_button:
        email_validation_error = validate_user_name(email)
        if email_validation_error:
            st.error(email_validation_error)  # Show email validation error
        else:
            st.success("If your email is registered, a password reset link has been sent to your email address.")

# Handle form submission for Login
if submit_button:
    if user_name and password:
        user_name_validation_error = validate_user_name(user_name)
        if user_name_validation_error:
            st.error(user_name_validation_error)  
        else:
            password_validation_error = validate_password(password)
            if password_validation_error:
                st.error(password_validation_error)  
            else:
                if check_user_credentials(user_name, password):
                    st.success("Login Successful!")
                    st.write(f"Welcome back, {user_name}!")
                else:
                    st.error("Invalid user name or password. Please try again.")
    else:
        st.error("Please fill in both user name and password.")
