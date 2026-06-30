import re

from modules.auth.regex_patterns import (
    USERNAME_PATTERN,
    EMAIL_PATTERN,
    PASSWORD_PATTERN
)

from modules.auth.exceptions import *


class Validator:

    @staticmethod
    def validate_username(username):

        # sub()
        username = re.sub(r"\s+", "", username)

        # match()
        if not re.match(r"^[A-Za-z]", username):
            raise InvalidUsernameException(
                "Username must start with a letter."
            )

        # fullmatch()
        if not USERNAME_PATTERN.fullmatch(username):
            raise InvalidUsernameException(
                "Username must be 4-20 characters and contain only letters, numbers and underscores."
            )

        return username

    @staticmethod
    def validate_email(email):

        # split()
        parts = re.split("@", email)

        if len(parts) != 2:
            raise InvalidEmailException(
                "Email format is invalid."
            )

        # fullmatch()
        if not EMAIL_PATTERN.fullmatch(email):
            raise InvalidEmailException(
                "Invalid email address."
            )

        return email

    @staticmethod
    def validate_password(password):

        # search()
        if not re.search(r"[A-Z]", password):
            raise WeakPasswordException(
                "Password needs an uppercase letter."
            )

        if not re.search(r"[a-z]", password):
            raise WeakPasswordException(
                "Password needs a lowercase letter."
            )

        if not re.search(r"\d", password):
            raise WeakPasswordException(
                "Password needs a number."
            )

        if not re.search(r"[@$!%*?&]", password):
            raise WeakPasswordException(
                "Password needs a special character."
            )

        # findall()
        digits = re.findall(r"\d", password)

        if len(digits) < 1:
            raise WeakPasswordException(
                "Password must contain at least one digit."
            )

        # fullmatch()
        if not PASSWORD_PATTERN.fullmatch(password):
            raise WeakPasswordException(
                "Password must be at least 8 characters."
            )

        return password