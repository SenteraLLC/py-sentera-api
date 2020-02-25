import requests


def get_auth_token(email, password):
    """
    Returns authentication token needed by :code:`sentera.api` calls

    :param email: sentera email
    :param password: sentera password
    :return: **token** - authentication token
    """
    # The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
    query = {
        "session": {
            "email": email,
            "password": password,
            "platform_id": "API",
            "version_id": "1.0.0",
        }
    }

    request = requests.post("https://api.sentera.com/v1/sessions", json=query)
    if request.status_code != 200:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )

    result = request.json()
    auth_token = result["auth_token"]
    return auth_token
