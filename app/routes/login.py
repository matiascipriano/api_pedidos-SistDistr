from jose import JWTError, jwt
from passlib.context import CryptContext
from models.usuario import Usuario
from pydantic import BaseModel
from database import SessionLocal
from fastapi import APIRouter, Depends, Header, HTTPException, status
from helpers.logging import logger
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

# Configuración del secreto para firmar los tokens
SECRET_KEY = "SUPERDUPERSECRET"
ALGORITHM = "HS256"

# Manejo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelo del usuario para representar lo que extraemos del token (el user id)
class TokenData(BaseModel):
    user_id: int

# Modelo del token
class Token(BaseModel):
    access_token: str
    token_type: str
    
# Modelo del login
class LoginData(BaseModel):
    username: str
    password: str

# Función para decodificar el token y obtener los datos del usuario
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        print (f"Obteniendo usuario actual")
        print (f"Token: {token}")
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        print (f"Usuario ID: ", user_id)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Credenciales invalidas")
        # Retornar el ID del usuario decodificado
        return TokenData(user_id=user_id)
    except Exception as e:
        logger.error(f"Error al decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token, tags=["admin", "centro"], description="Loguea un usuario y devuelve un token de acceso para utilizar los endpoints protegidos")
async def login(loginData: LoginData, db: Session = Depends(get_db)):
    logger.info(f"Intento de login de usuario {loginData.username}")
    username = loginData.username
    password = loginData.password
    user = Usuario.obtener_usuario_por_nombre_usuario(username, db)
    if user == None:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    elif not pwd_context.verify(password, user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
   # login_bonitasoft(username, password)
    logger.info(f"Usuario {username} logueado correctamente")
    # Incluye el rol en el token
    print(type(user.idusuario))
    token_data = {"sub": str(user.idusuario)}
    access_token = create_access_token(data=token_data)
    return Token(access_token=access_token, token_type="bearer")
