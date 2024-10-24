from routes import login
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from models.pedido import Pedido
from models.centro import Centro
from database import SessionLocal
from helpers.logging import logger
from pydantic import BaseModel
from typing import Optional, List


# Tener una session nueva para cada consulta
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

router = APIRouter()

class ItemDB(BaseModel):
    material : str
    cantidad : int

class PedidoDB(BaseModel):
    cliente : str
    items : List[ItemDB]

class CentroDB(BaseModel):
    ## En la BD el nombre esta uppercase
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
            raise Exception("No se encontraron pedidos en la base de datos.")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

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
            raise Exception(f"No se encontraron pedidos en estado {estado}")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")
    
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
        if (estado not in ["generado", "tomado","enviado", "entregado"]):
            raise Exception("Estado invalido.")
        # Cambiando estado del pedido
        logger.info(f"Cambiando estado del pedido {id} a {estado}")
        pedido = Pedido.cambiar_estado_pedido(id, estado, db)
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")
    
# Metodo GET para obtener los pedidos disponibles o disponibles filtrando por material
# GET - /pedidos/disponibles
@router.get("/disponibles", response_model=None, tags=["centro"])
def get_pedidos_disponibles(request: Request, db: Session = Depends(get_db), material : Optional[str] = None):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Obteniendo pedidos disponibles
        if material is None:
            logger.info(f"Devolviendo pedidos disponibles")
            pedidos = Pedido.devolver_pedidos_por_estado("generado", db)
        else:
            logger.info(f"Devolviendo pedidos con material {material}")
            pedidos = Pedido.devolver_pedidos_por_material(material, db)
        if (pedidos == None):
            raise Exception(f"No se encontraron pedidos disponibles")
        return pedidos
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

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
        nombre_centro = centro.nombre_centro.upper()
        logger.info(f"Tomando pedido {id} para {nombre_centro}")
        pedido = Pedido.devolver_pedido(id, db)
        if (pedido == None):
            logger.error(f"No se encontro el pedido")
            raise Exception("No se encontro el pedido")
        if (pedido.estado != "generado"):
            logger.error(f"El pedido no esta disponible")
            raise Exception("El pedido no esta disponible")
        centro_db = Centro.devolver_centro_por_nombre(nombre_centro, db)
        if (centro_db == None):
            logger.info(f"Registrando {nombre_centro}")
            centro = Centro.insertar_centro(nombre_centro, centro.direccion, db)

        pedido = Pedido.cambiar_estado_pedido_centro(id, "tomado", centro_db.idcentro, db)
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")


# Metodo PUT para cancelar un pedido
# PUT - /pedidos/cancelar/{id}
@router.put("/cancelar/{id}", response_model=None, tags=["centro"])
def cancelar_pedido(id: int, centro: CentroDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Tomando pedido
        nombre_centro = centro.nombre_centro.upper()
        logger.info(f"Cancelando pedido {id} para {nombre_centro}")
        pedido=cambiar_estado(id, 'generado', centro, db, update_centro=True)        
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

# Metodo PUT para enviar un pedido
# PUT - /pedidos/enviar/{id}
@router.put("/enviar/{id}", response_model=None, tags=["centro"])
def enviar_pedido(id: int, centro: CentroDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Tomando pedido
        nombre_centro = centro.nombre_centro.upper()
        logger.info(f"Pedido {id} enviado desde {nombre_centro}")
        pedido=cambiar_estado(id, 'enviado', centro, db)
        materiales = Pedido.devolver_materiales_pedido(id, db)
        centro = Centro.referenciar_materiales(nombre_centro, materiales, db)
        logger.info(f"Referenciando {nombre_centro}")
        centro = Centro.referenciar_materiales(nombre_centro, materiales, db)
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

# Metodo PUT para entregar un pedido
# PUT - /pedidos/entregar/{id}
@router.put("/entregar/{id}", response_model=None, tags=["admin"])
def entregar_pedido(id: int, centro: CentroDB, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Tomando pedido
        nombre_centro = centro.nombre_centro.upper()
        logger.info(f"Pedido {id} entregado desde {nombre_centro}")
        pedido=cambiar_estado(id, 'entregado', centro, db, estado_previo='enviado')        
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")
    
# Metodo GET para obtener un pedido por su id
# GET - /pedidos/info/{id}
@router.get("/info/{id}", response_model=None, tags=["centro"])
def get_pedido_por_id(id: int, request: Request, db: Session = Depends(get_db)):
    try:
        token = request.headers.get("Authorization").split()[1]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Falta authorization header")
    login.get_current_user(token)
    try:
        # Obteniendo pedido por id
        logger.info(f"Devolviendo pedido {id}")
        pedido = Pedido.devolver_pedido(id, db)
        if (pedido == None):
            raise Exception(f"No se encontro el pedido")
        return pedido
    except Exception as e:
        logger.error(f"Hubo una excepcion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor. {e}")

def cambiar_estado(id, estado, centro, db: Session = Depends(get_db), update_centro=False, estado_previo="tomado"):
    pedido = Pedido.devolver_pedido(id, db)
    if (pedido == None):
        raise Exception("No se encontro el pedido")
    if (pedido.estado != estado_previo):
        raise Exception("El pedido no esta disponible")
    nombre_centro = centro.nombre_centro.upper()
    centro = Centro.devolver_centro_por_nombre(nombre_centro, db)
    if (pedido.idcentro == centro.idcentro):
        centro_id = None if update_centro else centro.idcentro  
        pedido = Pedido.cambiar_estado_pedido_centro(id, estado, centro_id, db)
    else:
         raise Exception("El pedido no corresponde al centro")
    return pedido