from main import SECRET_KEY, ALGORITHM, oauth2_scheme
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from models.usuario import Usuario

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = Usuario.obtener_usuario(payload.get("sub"))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")