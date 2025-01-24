#!/usr/bin/env python3

#token : eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOiAxNjg2NzY1Mjk1LCAiZXhwIjogMTY4Njc2NTg5NSwgImlzcyI6ICIzNDY3NjYifQ.Z5eqVc6f8DSRLrFY3knCXkTTX1lMlj1Arp0oB4OgF2K34FyIyi4hu2t9f3qg4MQO31oMoW9GWnIxJZXLCDrFPML_H__2qs2MLHNHBa9EN1a_ooifAKT4-FCAYHjZF4HbIfnFUEpLDQli0ptj6JHRqYWEUaai57OCJA-ps_M98BEYozuwOlZn0_kUIsV7JmaiV4gaLw-tbRNb2-DYv5kPRA84R87hBifC_4WikDuXczvpUqotQWSKRLPBkjAFlPl4vjM9R4GrCHYXeGYEL1eHwbV6cAGMmSlUNgBnsIYwaY_2r8Oygrd6xzxNj7zjtKauB29pkP2-JcigbczDOIL14Q
import os
from typing import Any
# import jwt
import time
from datetime import datetime, timezone, timedelta
import logging
from jwt import jwk, JWT

class GenerateJWT:
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pem="utils/repository_monitor_app_pk.pem"
        app_id=346766

        # Open PEM
        with open(pem, 'rb') as pem_file:
            pem_data = pem_file.read()

            # Verify if it's a private key
            try:
                signing_key = jwk.jwk_from_pem(pem_data)  # Try loading as private key
            except ValueError as e:
                raise ValueError(f"Invalid PEM format: {e}")

        payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's identifier
            'iss': app_id
        }

        # Create JWT
        jwt_instance = JWT()
        encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')
        return encoded_jwt