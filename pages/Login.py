import streamlit as st

from modules.auth.auth import Authentication

st.set_page_config(
    page_title="Login"
)

st.title("Mnemosyne")

st.subheader("Login")

email = st.text_input(
    "Email"
)

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login", use_container_width=True):

    try:

        user = Authentication.login(
            email,
            password
        )

        st.session_state.logged_in = True
        st.session_state.username = user[1]
        st.session_state.email = user[2]

        st.success("Login Successful!")

        st.switch_page("app.py")

    except Exception as e:

        st.error(str(e))

st.divider()

st.write("Don't have an account?")

if st.button(
    "Register",
    use_container_width=True
):
    st.switch_page("pages/Register.py")