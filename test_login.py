from modules.auth.auth import Authentication

try:

    user = Authentication.login(

        "pree@gmail.com",

        "Password@123"

    )

    print("Welcome")

    print(user)

except Exception as e:

    print(e)