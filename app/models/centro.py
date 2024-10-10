from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import Session
from database import Base

class Centro(Base):
    __tablename__ = 'centro'

    idcentro = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = Column(String(45), nullable=False)
    direccion = Column(String(45), nullable=False)

    def devolver_centro(id, db: Session):
        try:
            centro = db.query(Centro).filter(Centro.idcentro == id).first()
            return centro.nombre
        except Exception as e:
            raise Exception(f"Error al devolver el centro: {e}")
        
    def devolver_centros_todos(db: Session):
        centros = db.query(Centro).all()
        return centros
        
    def devolver_centro_por_nombre(nombre, db: Session):
        try:
            centro = db.query(Centro).filter(func.lower(Centro.nombre) == nombre.lower()).first()
            return centro
        except Exception as e:
            raise (f"Error al devolver el centro: {e}")

    def insertar_centro(nombre, direccion, db: Session):
        try:
            centro = Centro(nombre=nombre, direccion=direccion)
            db.add(centro)
            db.commit()
            db.refresh(centro)
            return centro
        except Exception as e:
            raise Exception(f"Error al insertar el centro: {e}")