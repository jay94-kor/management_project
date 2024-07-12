import streamlit as st
import requests
from requests_oauthlib import OAuth2Session

# NaverWorks OAuth settings
client_id = "your_client_id"
client_secret = "your_client_secret"
authorization_url = "https://nid.naver.com/oauth2.0/authorize"
token_url = "https://nid.naver.com/oauth2.0/token"

# NaverWorks OAuth scope
scope = ["email", "profile"]

def get_naverworks_token():
    # Create an OAuth2Session instance
    oauth = OAuth2Session(client_id, scope=scope)

    # Redirect the user to the authorization URL
    authorization_url, state = oauth.authorization_url(authorization_url)
    st.write(f"Please go to this URL to authorize: {authorization_url}")
    st.write("After authorization, enter the authorization code below.")

    # Get the authorization code from the user
    authorization_code = st.text_input("Authorization Code")

    # Fetch the token
    token = oauth.fetch_token(token_url, code=authorization_code)

    # Return the token
    return token

def get_naverworks_user_info(token):
    # Use the token to fetch user info
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    response = requests.get("https://openapi.naverworks.com/v1/users/me", headers=headers)
    user_info = response.json()
    return user_info

def authenticate():
    # Get the token
    token = get_naverworks_token()

    # Get the user info
    user_info = get_naverworks_user_info(token)

    # Check if the user is an admin
    is_admin = user_info["email"] == "admin_email@example.com"

    # Store the user info and admin status in the session state
    st.session_state["user"] = user_info
    st.session_state["is_admin"] = is_admin

    # Show a success message
    st.success("Successfully authenticated!")

def login():
    st.sidebar.title("로그인")
    authenticate()

def logout():
    st.sidebar.title("로그아웃")
    if st.sidebar.button("로그아웃"):
        st.session_state.pop("user", None)
        st.session_state.pop("is_admin", None)
        st.sidebar.success("성공적으로 로그아웃 되었습니다.")