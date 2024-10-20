from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.usuario import Usuario
from database import SessionLocal
from pydantic import BaseModel
from helpers.logging import logger
from routes.login import pwd_context
from routes import login

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

class UsuarioInDB(BaseModel):
    usuario: str
    contraseña: str
    nombre_completo: str

# Metodo GET para obtener todos los usuarios existentes en la db
# GET - /usuarios/todos
@router.get("/todos", response_model=None, tags=["admin"])
def get_usuarios_todos(db: Session = Depends(get_db)):
    logger.info("Devolviendo todos los usuarios")
    try:
        # Obteniendo todos los usuarios
        usuarios = Usuario.devolver_usuarios(db)
        if (usuarios == None):
            raise HTTPException(status_code=404, detail="No se encontraron usuarios en la base de datos.")
        return usuarios
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
    
# Metodo POST para generar un nuevo usuario en la base datos
# POST - /usuarios/insertar
@router.post("/insertar", response_model=None, tags=["admin"])
def insertar_usuario(usuario: UsuarioInDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    # Verificando que el usuario no exista
    if(Usuario.obtener_usuario_por_nombre_usuario(usuario.usuario.lower(),db)):
        logger.error(f"El usuario {usuario} ya existe")
        raise HTTPException(status_code=500, detail=f"Ya existe este usuario bajo el nombre: {usuario.usuario}")
    try:
        # Insertando nuevo usuario en la db
        logger.info(f"Insertando usuario: {usuario.usuario}")
        hash_pass = pwd_context.hash(usuario.contraseña)
        usuario.contraseña = hash_pass
        usuario = Usuario.insertar_usuario(usuario, db)
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo usuario. {e}")