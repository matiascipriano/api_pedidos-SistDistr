from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from fastapi import HTTPException
from database import Base
from models.item import Item
from models.centro import Centro
from models.material import Material
from helpers.logging import logger


class Pedido(Base):
    __tablename__ = 'pedido'

    idpedido = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    estado = Column(String(20), nullable=False)
    cliente = Column(String(100), nullable=False)
    # Este campo sera null si el pedido no esta "tomado"
    idcentro = Column(Integer, ForeignKey('centro.idcentro'), nullable=True)
    # Relaciones
    centro = relationship("Centro")
    ## Relación uno-a-muchos con Item
    items = relationship("Item", back_populates="pedido", cascade="all, delete-orphan")

    def devolver_pedido(id, db: Session):
        try:
            pedido = db.query(Pedido).filter(Pedido.idpedido == id).first()
            return pedido
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al devolver el pedido: {e}")

    def devolver_pedidos_todos(db: Session):
        try:
            pedidos = db.query(Pedido).all()
            return pedidos
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al devolver los pedidos: {e}")

    def devolver_pedidos_por_estado(estado, db: Session):
        try:
            response = []
            pedidos = db.query(Pedido).filter(Pedido.estado == estado).all()
            for pedido in pedidos:
                obj = {
                    "Pedido": pedido.idpedido,
                    "Estado": pedido.estado,
                    "Cliente": pedido.cliente
                }
                if ((estado == "tomado" or estado=='enviado')and pedido.idcentro is not None):
                    obj["Centro"] = Centro.devolver_centro(pedido.idcentro, db)
                response.append(obj)
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")
        
    def insertar_pedido(data, db: Session):
        try:
            items =[]
            for mat in data.items:
                material = Material.devolver_material_por_nombre(mat["material"], db)
                item = Item(
                    idmaterial=int(material.idmaterial),
                    cantidad=int(mat["cantidad"])
                )
                items.append(item)
            pedido = Pedido(estado="generado", cliente=data.cliente,items=items)
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            logger.error(f"Error en modelo pedido. {e}")
            raise HTTPException(status_code=500, detail=f"Error al insertar recoleccion: {e}")
        
    def cambiar_estado_pedido(id, estado, db):
        try:
            pedido = db.query(Pedido).filter(Pedido.idpedido == id).first()
            if pedido == None:
                raise HTTPException(status_code=404, detail="No se encontro el pedido")
            pedido.estado = estado
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            logger.error(f"Error actualizando pedido {id}. {e}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar estado del pedido: {e}")
        
    def cambiar_estado_pedido_centro(id, estado, centro, db):
        try:
            pedido = db.query(Pedido).filter(Pedido.idpedido == id).first()
            if pedido == None:
                raise HTTPException(status_code=404, detail="No se encontro el pedido")
            pedido.estado = estado
            pedido.idcentro = centro
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            logger.error(f"Error actualizando pedido {id}. {e}")
            raise HTTPException(status_code=500, detail=f"Error al cambiar estado del pedido: {e}")
        
    def devolver_materiales_pedido(id, db):
        try:
            items = db.query(Item).filter(Item.idpedido == id).all()
            materiales = []
            for item in items:
                material = Material.devolver_material(item.idmaterial, db)
                materiales.append(material)
            return materiales
        except Exception as e:
            logger.error(f"Error devolviendo materiales del pedido {id}. {e}")
            raise HTTPException(status_code=500, detail=f"Error al devolver materiales del pedido: {e}")
    

    def devolver_pedidos_por_material(nombre, db: Session):
        try:
            material = Material.devolver_material_por_nombre(nombre, db)
            pedidos = (
            db.query(Pedido)
            .join(Item, Pedido.idpedido == Item.idpedido)
            .filter(Item.idmaterial == material.idmaterial)
            .filter(Pedido.estado == "generado")
            .all()
             )
            return pedidos
        except Exception as e:
            logger.error(f"Error en modelo pedido. {e}")
            raise HTTPException(status_code=500, detail=f"Error al insertar recoleccion: {e}")

    def devolver_pedidos_por_centro(db: Session, estado=None, centro =None):
        try:
            if centro is not None:
                query = db.query(Pedido).filter(Pedido.idcentro == centro)
            else:
                query = db.query(Pedido).filter(Pedido.idcentro != None)
    
            if estado is not None and estado in ["tomado", "enviado","entregado"]:
                query = query.filter(Pedido.estado == estado)

            pedidos = query.all()
            return pedidos
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")
     