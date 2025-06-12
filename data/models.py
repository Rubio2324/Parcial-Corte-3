# data/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import date

Base = declarative_base()

# Esquemas Pydantic para validación de datos de entrada (Create/Update)
# y para la estructura base de los modelos de respuesta.

class UsuarioBase(BaseModel):
    nombre: str
    edad: int
    nacionalidad: str

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(UsuarioBase):
    eliminado_logico: bool = False
    nombre: Optional[str] = None
    edad: Optional[int] = None
    nacionalidad: Optional[str] = None

# --- NUEVOS ESQUEMAS PYDANTIC PARA RESPUESTAS API ---
class UsuarioResponse(UsuarioBase):
    id: int
    eliminado_logico: bool

    class Config:
        from_attributes = True # Permite que Pydantic lea datos de objetos ORM

class MascotaBase(BaseModel):
    nombre: str
    tipo: str
    raza: str
    imagen_url: Optional[HttpUrl] = None # Mantenemos la URL para la imagen del equipo

class MascotaCreate(MascotaBase):
    pass

class MascotaUpdate(MascotaBase):
    eliminado_logico: bool = False
    nombre: Optional[str] = None
    id_usuario : Optional [int] = None
    tipo: Optional[str] = None
    raza: Optional[str] = None
    imagen_url: Optional[HttpUrl] = None

class MascotaResponse(MascotaBase):
    id: int
    eliminado_logico: bool

    class Config:
        from_attributes = True

class VueloBase(BaseModel):
    origen : str
    destino: str
    fecha: date

class VueloCreate(VueloBase):
    pass

class VueloUpdate(VueloBase):
    id_usuario: Optional[int] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    fecha: Optional[date] = None
    eliminado_logico: bool = False

class VueloResponse(VueloBase):
    id: int
    eliminado_logico: bool

    class Config:
        from_attributes = True

# --- Modelos SQLAlchemy (mapeo a la base de datos) ---
class Usuario(Base):
    __tablename__ = "Usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    nacionalidad = Column(String)
    eliminado_logico = Column(Boolean, default=False)

    mascota_obj = relationship("Mascota", back_populates="usuario_obj")
    vuelo_obj = relationship("Vuelo", back_populates="usuario_obj")

    # No necesitamos Config aquí para el modelo ORM,
    # ya que los Pydantic Response Models se encargan de la serialización.

class Mascota(Base):
    __tablename__ = "Mascotas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"))
    tipo = Column(String)
    raza = Column(String)
    imagen_url = Column(String, nullable=True) # Almacenamos la URL como String
    eliminado_logico = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="mascota_obj")

class Vuelo(Base):
    __tablename__ = "Vuelos"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"))
    origen = Column(String)
    destino = Column(String)
    fecha = Column(Date)
    eliminado_logico = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="vuelo_obj")

    # No necesitamos Config aquí para el modelo ORM.
