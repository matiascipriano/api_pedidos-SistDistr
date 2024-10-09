from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from fastapi import HTTPException
from database import Base
from helpers.logging import logger

class Usuario(Base):
    __tablename__ = 'usuario'

    idUsuario = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    usuario = Column(String(20), nullable=False)
    contraseña = Column(String(255), nullable=False)
    nombre_completo = Column(String(100), nullable=False)
       
    def insertar_usuario(data, db: Session):
        try:
            usuario = Usuario(usuario=data.usuario, contraseña=data.contraseña, nombre_completo=data.nombre_completo)
            logger.info(f"Insertando usuario: {usuario.usuario} || {usuario.nombre_completo} || {usuario.contraseña}")
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            return usuario
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al insertar el usuario: {e}")
        
    def devolver_usuarios(db: Session):
        try:
            usuarios = db.query(Usuario).all()
            return usuarios
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al devolver los usuarios: {e}")
                
    def devolver_usuario(id,db: Session):
        try:
            usuario = db.query(Usuario).filter(Usuario.idUsuario == id).first()
            return usuario
        except Exception as e:
            logger.error(f"Error al devolver el usuario: {e}")
            raise HTTPException(status_code=500, detail=f"Error al devolver el usuario: {e}")
    
    def obtener_usuario_por_nombre_usuario(usuario: str, db: Session):
        usuario = db.query(Usuario).filter(Usuario.usuario == usuario).first()
        return usuario