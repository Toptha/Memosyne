from modules.auth.auth import Authentication

try:

    message = Authentication.register(

        username="Pree",

        email="pree@gmail.com",

        password="Password@123",

        confirm_password="Password@123"

    )

    print(message)

except Exception as e:

    print(e)