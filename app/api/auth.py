import os

from fastapi import APIRouter, HTTPException, Header, status, Depends
from pydantic import BaseModel
import bcrypt
import jwt
import datetime

from dotenv import load_dotenv

from app.core.database import get_db_client

load_dotenv()

router = APIRouter(prefix='/auth')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

class UsuarioAuth(BaseModel):
    email: str
    password: str
    name: str
    username: str

class UsuarioLogin(BaseModel):
    email: str
    password: str


def verificar_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hubo un error, intentalo de nuevo"
        )
    try:
        token = authorization.split(" ")[1]
        usuario_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return usuario_jwt
        
    except (jwt.PyJWTError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hubo un error, intentalo de nuevo"
        )

@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro(user: UsuarioAuth):
    # Encriptación directa con bcrypt
    salt = bcrypt.gensalt()
    # haspw requiere bytes, por lo que codificamos el string. Luego decodificamos el resultado para guardarlo como string en DB.
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')

    try:
        with get_db_client() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, name, username) VALUES (%s, %s, %s, %s)",
                (user.email, password_hash, user.name, user.username)
            )
        return {"message": "Usuario registrado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar el usuario")

@router.post("/login")
def login(user: UsuarioLogin):
    try:
        with get_db_client() as cur:
            cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s", (user.email,))
            usuario_loggeado = cur.fetchone()

        if not usuario_loggeado:
            raise HTTPException(status_code=401, detail="Hubo un error, revisa bien tu correo y contraseña")

        user_id, user_email, db_password_hash = usuario_loggeado

        # checkpw requiere que tanto la contraseña ingresada como el hash de la DB sean bytes
        if not bcrypt.checkpw(user.password.encode('utf-8'), db_password_hash.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        payload = {
            "id": user_id,
            "email": user_email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "message": "Login exitoso",
            "access_token": access_token
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al iniciar sesión")

'''
@router.get("/ruta-protegida")
def ruta_protegida(usuario: dict = Depends(verificar_token)):
    return {"message": "Tienes acceso", "datos_usuario": usuario}
'''