import json
import time
from typing import Dict
import cryptocode
from jose import jwt



PAYLOAD_SECRET = "ubF5I41SuaVY2wmTnz43qA"
JWT_SECRET = "3a2c3158a8a428c1a0c1998360f7e452"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {"access_token": token}

def encodePayload(payload):
    converted = json.dumps(payload)
    encoded_text = cryptocode.encrypt(converted, PAYLOAD_SECRET)
    return encoded_text

def decodePayload(payload):
    decoded = cryptocode.decrypt(payload, PAYLOAD_SECRET)
    return decoded

def signJWT(user_id: str, role: str, school_code: str) -> Dict[str, str]:
    expiration_duration = 60 * 60 * 24
    data = {"user_id": user_id, "role": role, "expires": time.time() + expiration_duration, "school_code": school_code}
    payload = {"data": encodePayload(data)}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decodeJWT(token: str, access_levels) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        decoded_payload = json.loads(decodePayload(decoded_token["data"]))
        if decoded_payload["expires"] >= time.time():
            if access_levels and decoded_payload["role"] in access_levels:
                return decoded_payload
            elif not access_levels:
                return decoded_payload
            else:
                return {"error": "unauthorized"}
        else:
            return {"error": "token expired"}
    except Exception as e:
        return {}
