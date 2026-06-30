import streamlit as st

from modules.auth.auth import Authentication

st.set_page_config(
    page_title="Register"
)

st.title("Mnemosyne")

st.subheader("Create Account")

username = st.text_input(
    "Username"
)

email = st.text_input(
    "Email"
)

password = st.text_input(
    "Password",
    type="password"
)

confirm_password = st.text_input(
    "Confirm Password",
    type="password"
)

if st.button(
    "Register",
    use_container_width=True
):

    try:

        Authentication.register(
            username,
            email,
            password,
            confirm_password
        )

        st.success(
            "Registration Successful!"
        )

        st.info(
            "Redirecting to Login..."
        )

        st.switch_page(
            "pages/Login.py"
        )

    except Exception as e:

        st.error(str(e))

st.divider()

st.write("Already have an account?")

if st.button(
    "Login",
    use_container_width=True
):
    st.switch_page("pages/Login.py")