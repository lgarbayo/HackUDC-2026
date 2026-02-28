import jwt
import datetime
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "super_secreto_hackathon" # En producción iría en tu .env
security = HTTPBearer()

# Usuarios hardcodeados con contraseñas pre-encriptadas (admin123 y normal123)
USERS = {
    "admin": {"password": pwd_context.hash("admin123"), "role": "admin"},
    "empleado": {"password": pwd_context.hash("normal123"), "role": "normal"}
}

def create_token(username: str, role: str):
    # El payload es el cuerpo del token que contiene los datos del usuario
    payload = {
        "sub": username, 
        "role": role, 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload # Retorna el diccionario con 'sub' y 'role'
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Token inválido o expirado")