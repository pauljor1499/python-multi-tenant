from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.authentication import jwt_handler


class JWTBearer(HTTPBearer):
    def __init__(self, access_levels, auto_error: bool = True):
        self.access_levels = access_levels
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        credentials.credentials = credentials.credentials.replace('"', "")

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            verification = self.verify_jwt(credentials.credentials, self.access_levels)
            if not verification:
                raise HTTPException(status_code=403, detail="Invalid token")

            request.state.user_data = jwt_handler.decodeJWT(credentials.credentials, self.access_levels)
            return credentials.credentials
        
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str, access_levels) -> bool:
        isTokenValid = False
        try:
            payload = jwt_handler.decodeJWT(jwtoken, access_levels)
        except:
            payload = None

        if payload and "error" in payload:
            if payload["error"] == "unauthorized":
                raise HTTPException(status_code=403, detail="Access denied")
            if payload["error"] == "token expired":
                raise HTTPException(status_code=403, detail="Token expired")
            
        if payload:
            isTokenValid = True
        return isTokenValid
