import os
import base64
import logging

import falcon
import jwt


class TokenAuthMiddleware(object):
    def process_request(self, req, resp):
        # check if authorization header exists
        auth_header = req.get_header("Authorization")

        # check if the auth header was set
        if auth_header is None:
            raise falcon.HTTPUnauthorized("Authentication required")
        else:
            auth_fields = auth_header.split()
            if len(auth_fields) != 2:
                raise falcon.HTTPUnauthorized("Authentication validation error")
            else:
                # parsing credentials
                auth_credentials = (
                    base64.b64decode(auth_fields[1]).decode("utf-8").split(":")
                )
                # check there is a username and password
                if len(auth_credentials) != 2:
                    raise falcon.HTTPUnauthorized("Authentication validation error")
                else:
                    # checking token is valid
                    username, token = auth_credentials
                    try:
                        # decode the payload
                        payload = jwt.decode(
                            token, os.getenv("TIMONE_TOKEN_SECRET"), algorithms="HS256"
                        )
                        # check the payload username is the same as the one used
                        # for login
                        if (
                            payload.get("username") is None
                            or username != payload["username"]
                        ):
                            logging.error("Expecting {} but the token was for {}".format(username, payload.get("username")) )
                            raise falcon.HTTPUnauthorized("Token validation error")
                        else:
                            logging.debug("{} logged in.".format(username))

                    except jwt.exceptions.DecodeError:
                        logging.error("Token cannot be decoded.")
                        raise falcon.HTTPUnauthorized("Token validation error")
                    except jwt.ExpiredSignatureError:
                        logging.error("Token is expired.")
                        raise falcon.HTTPUnauthorized("Token validation error")
                    except jwt.InvalidIssuerError:
                        logging.error("Token has invalid issuer.")
                        raise falcon.HTTPUnauthorized("Token validation error")
