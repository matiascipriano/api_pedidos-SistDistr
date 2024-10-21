from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.centro import Centro
from database import SessionLocal
from helpers.logging import logger
from routes import login
from models.pedido import Pedido
from pydantic import BaseModel

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

class CentroDB(BaseModel):
    nombre_centro : str
    direccion: str


# Metodo GET para obtener todos los centros existentes en la db
# GET - /centros/todos
@router.get("/todos", response_model=None, tags=["admin"])
def get_centros_todos(db: Session = Depends(get_db)):
    logger.info("Devolviendo todos los centros")
    try:
        # Obteniendo todos los centros de recoleccion
        centros = Centro.devolver_centros_todos(db)
        if (centros == None):
            raise HTTPException(status_code=404, detail="No se encontraron centros de recolección en la base de datos.")
        return centros
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo POST para insertar un nuevo centro de recoleccion
# POST - /centros/insertar
@router.post("/insertar", response_model=None, tags=["admin"])
def insertar_centro(nombre: str, request: Request, direcc: str, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    # Verificando que el centro no exista
    if (Centro.devolver_centro_por_nombre(nombre,db) != None):
        logger.error(f"El grupo {nombre} ya existe")
        return {"detail": f"Ya existe este centro de recolección bajo el nombre: {centro.nombre}"}
    try:
        # Insertando nuevo centro en la db
        logger.info(f"Insertando grupo: {nombre}")
        centro = Centro.insertar_centro(nombre, direcc, db)
        return centro
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo centro de recoleccion. {e}")


# Metodo GET para obtener todos los pedidos para el centro
# GET - /centros/pedidos/{centro}
@router.get("/pedidos/{idcentro}", response_model=None, tags=["centro"])
def get_centros_todos(idcentro,request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    logger.info("Devolviendo todos los pedidos para el centro")
    try:
        pedidos = Pedido.devolver_pedidos_por_centro(idcentro,db)
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo GET para obtener todos los pedidos para el centro con un estado especifico
# GET - /centros/pedidos/{estado}/{centro}
@router.get("/pedidos/{estado}/{idcentro}", response_model=None, tags=["centro"])
def get_centros_todos(estado,idcentro, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        if (estado not in ["tomado", "entregado"]):
            raise HTTPException(status_code=422, detail="Estado invalido.")
        pedidos = Pedido.devolver_pedidos_por_centro(idcentro,db,estado)
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
