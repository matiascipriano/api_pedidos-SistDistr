from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from database import Base

class Material(Base):
    __tablename__ = 'material'

    idMaterial = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = Column(String(45), nullable=False)
    descripcion = Column(String(45), nullable=False)

    def devolver_material(id, db: Session):
        try:
            material = db.query(Material).filter(Material.idMaterial == id).first()
            return material.nombre
        except Exception as e:
            raise (f"Error al devolver el material: {e}")
        
    def devolver_materiales_todos(db: Session):
        try:
            materiales = db.query(Material).all()
            return materiales
        except Exception as e:
            raise (f"Error al devolver los materiales: {e}")
        
    def devolver_material_por_nombre(nombre, db: Session):
        try:
            material = db.query(Material).filter(Material.nombre == nombre).first()
            return material
        except Exception as e:
            raise (f"Error al devolver el material: {e}")
        
    def insertar_material(nombre, db: Session):
        try:
            material = Material(nombre=nombre)
            db.add(material)
            db.commit()
            db.refresh(material)
            return material
        except Exception as e:
            raise (f"Error al insertar el material: {e}")