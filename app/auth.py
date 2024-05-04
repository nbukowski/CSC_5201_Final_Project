import jwt
from datetime import datetime, timedelta

class Auth:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def create_token(self, user_id):
        """
        Create a JWT token for the given user ID.
        :param user_id: The unique identifier of the user.
        :param expiration_minutes: Expiration time of the token in minutes.
        :return: JWT token as a string.
        """
        payload = {
            'user_id': user_id
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def verify_token(self, token):
        """
        Verify the JWT token.
        :param token: JWT token as a string.
        :return: Decoded payload if the token is valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
