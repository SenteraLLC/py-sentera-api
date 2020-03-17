"""Functions to generate authorization credentials for use of the Sentera Weather API."""
import requests

from sentera import configuration

def get_auth_token(email, password):
    """
    Return an access token needed by :code:`sentera.api` calls.

    :param email: sentera email
    :param password: sentera password
    :return: **token** - access token
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

    request = requests.post(configuration.sentera_api_url('/v1/sessions'), json=query)
    if request.status_code != 200:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )

    result = request.json()
    auth_token = result["auth_token"]
    return auth_token

def get_application_token(client_id, client_secret):
    """
    Return an access token needed by :code:`sentera.api` calls.

    :param client_id: client id from a CloudVault application
    :param client_secret: client secret from a CloudVault application
    :return: **token** - access token
    """

    data = { 'grant_type': 'client_credentials'}
    response = requests.post(
        configuration.sentera_api_url('/oauth/token'),
        data=data, allow_redirects=False, auth=(client_id, client_secret)
    )
    if response.status_code != 200:
        raise Exception(
            "Failed to authenticate using client credentials. Response code of {} and message: {}".format(
                response.status_code, response.json()
            )
        )
    return response.json()
