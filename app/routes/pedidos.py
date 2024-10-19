from routes import login
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.pedido import Pedido
from models.centro import Centro
from database import SessionLocal
from helpers.logging import logger
from pydantic import BaseModel

# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

class PedidoDB(BaseModel):
    estado : str
    cliente : str
    # [ {"material": "nombre_material", "cantidad": int}, {...} ]
    items : list

class CentroDB(BaseModel):
    nombre_centro : str
    direccion: str

# Metodo GET para obtener todos los pedidos existentes en la db
# GET - /pedidos/todos
@router.get("/todos", response_model=None, tags=["admin"])
def get_pedidos_todos(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    logger.info("Devolviendo todos los pedidos")
    try:
        # Obteniendo todos los pedidos
        pedidos = Pedido.devolver_pedidos_todos(db)
        if (pedidos == None):
            raise HTTPException(status_code=404, detail="No se encontraron pedidos en la base de datos.")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo POST para insertar un nuevo pedido
# POST - /pedidos/insertar
@router.post("/insertar", response_model=None, tags=["admin"])
def insertar_pedido(pedido: PedidoDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Insertando nuevo pedido en la db
        logger.info(f"Insertando pedido para {pedido.cliente}")
        pedido = Pedido.insertar_pedido(pedido, db)
        return pedido
    except Exception as e:
        logger.error(f"Error insertando nuevo pedido. {e}")
        raise HTTPException(status_code=500, detail=f"Error insertando nuevo pedido. {e}")
    
# Metodo GET para obtener los pedidos a partir de un estado
# GET - /pedidos/estado/{estado}
@router.get("/estado/{estado}", response_model=None, tags=["admin"])
def get_pedidos_por_estado(estado: str, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Obteniendo pedidos por estado
        logger.info(f"Devolviendo pedidos en estado {estado}")
        pedidos = Pedido.devolver_pedidos_por_estado(estado, db)
        if (pedidos == None):
            raise HTTPException(status_code=404, detail=f"No se encontraron pedidos en estado {estado}")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
    
# Metodo PUT para cambiar el estado de un pedido
# PUT - /pedidos/estado/{id}
@router.put("/estado/{id}", response_model=None, tags=["admin"])
def cambiar_estado_pedido(id: int, estado: str, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        if (estado not in ["generado", "tomado", "entregado"]):
            raise HTTPException(status_code=422, detail="Estado invalido.")
        # Cambiando estado del pedido
        logger.info(f"Cambiando estado del pedido {id} a {estado}")
        pedido = Pedido.cambiar_estado_pedido(id, estado, db)
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
    
# Metodo GET para obtener los pedidos disponibles
# GET - /pedidos/disponibles
@router.get("/disponibles", response_model=None, tags=["centro"])
def get_pedidos_disponibles(request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Obteniendo pedidos disponibles
        logger.info(f"Devolviendo pedidos disponibles")
        pedidos = Pedido.devolver_pedidos_por_estado("generado", db)
        if (pedidos == None):
            raise HTTPException(status_code=404, detail="No se encontraron pedidos disponibles")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

# Metodo PUT para tomar un pedido
# PUT - /pedidos/tomar/{id}
@router.put("/tomar/{id}", response_model=None, tags=["centro"])
def tomar_pedido(id: int, centro: CentroDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Tomando pedido
        logger.info(f"Tomando pedido {id} para {centro.nombre_centro}")
        pedido = Pedido.devolver_pedido(id, db)
        if (pedido == None):
            raise HTTPException(status_code=404, detail="No se encontro el pedido")
        if (pedido.estado != "generado"):
            raise HTTPException(status_code=422, detail="El pedido no esta disponible")
        materiales = Pedido.devolver_materiales_pedido(id, db)
        centro_nombre = centro.nombre_centro.upper()
        centro_db = Centro.devolver_centro_por_nombre(centro_nombre, db)
        if (centro_db == None):
            logger.info(f"Registrando {centro.nombre_centro}")
            centro = Centro.insertar_centro_con_materiales(centro.nombre_centro, centro.direccion, materiales, db)
        else:
            logger.info(f"Referenciando {centro.nombre_centro}")
            centro = Centro.referenciar_materiales(centro.nombre_centro, materiales, db)
        pedido = Pedido.cambiar_estado_pedido_centro(id, "tomado", centro_db.idcentro, db)
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")