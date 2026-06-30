import bcrypt

from data.database.database import get_connection

from models.user import User

from modules.auth.validator import Validator

from modules.auth.exceptions import (
    UserAlreadyExistsException,
    InvalidLoginException,
    PasswordMismatchException
)


class Authentication:

    @staticmethod
    def register(username, email, password, confirm_password):

        username = Validator.validate_username(username)
        email = Validator.validate_email(email)
        password = Validator.validate_password(password)

        if password != confirm_password:
            raise PasswordMismatchException(
                "Passwords do not match."
            )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

        if cursor.fetchone():

            conn.close()

            raise UserAlreadyExistsException(
                "User already exists."
            )

        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        cursor.execute(
            """
            INSERT INTO users
            (username,email,password)
            VALUES (?,?,?)
            """,
            (
                username,
                email,
                hashed_password.decode()
            )
        )

        conn.commit()
        conn.close()

        return "Registration Successful"

    @staticmethod
    def login(email, password):

        Validator.validate_email(email)

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if not user:

            raise InvalidLoginException(
                "User not found."
            )

        stored_password = user[3]

        if bcrypt.checkpw(
            password.encode(),
            stored_password.encode()
        ):

            return user

        raise InvalidLoginException(
            "Incorrect password."
        )