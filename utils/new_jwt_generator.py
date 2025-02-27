from datetime import datetime, timezone, timedelta
import os
import jwt
from typing import Any
import logging
from dotenv import load_dotenv
load_dotenv()


class NewGenerateJWT:
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        # pem = "/app/utils/repository_monitor_app_pk.pem"
        pem = os.getenv('PEM_FILE')
        client_id = os.getenv('CLIENT_ID')
        print("Pem", pem)
        print("Client", client_id)

        try:
            with open(pem, 'rb') as pem_file:
                signing_key = pem_file.read()
                payload = {
                    'iat': datetime.now(timezone.utc),
                    'exp': datetime.now(timezone.utc) + timedelta(seconds=600),
                    'iss': client_id
                }
                encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
                print("Token: ", encoded_jwt)
                pem_file.close()
            return encoded_jwt
        except Exception as e:
            logging.error(f"In get_github_jwt: {e}")
            return None

