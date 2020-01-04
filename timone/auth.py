import os
import base64

import falcon
import jwt


class TokenAuthMiddleware(object):
    def process_request(self, req, resp):
        # check if authorization header exists
        auth_header = req.get_header("Authorization")

        if auth_header is None:
            raise falcon.HTTPUnauthorized("Authentication required")
        else:
            auth_fields = auth_header.split()
            if len(auth_fields) != 2:
                raise falcon.HTTPUnauthorized("Authentication validation error")
            else:
                auth_credentials = (
                    base64.b64decode(auth_fields[1]).decode("utf-8").split(":")
                )
                if len(auth_credentials) != 2:
                    raise falcon.HTTPUnauthorized("Authentication validation error")
                else:
                    username, token = auth_credentials
                    try:
                        payload = jwt.decode(
                            token, os.getenv("TIMONE_TOKEN_SECRET"), algorithms="HS256"
                        )

                        if (
                            payload.get("username") is None
                            or username != payload["username"]
                        ):
                            raise falcon.HTTPUnauthorized("Token validation error")

                    except jwt.exceptions.DecodeError:
                        raise falcon.HTTPUnauthorized("Token validation error")
                    except jwt.ExpiredSignatureError:
                        raise falcon.HTTPUnauthorized("Token validation error")
                    except jwt.InvalidIssuerError:
                        raise falcon.HTTPUnauthorized("Token validation error")
