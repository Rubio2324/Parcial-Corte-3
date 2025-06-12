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
    mascota_id: int
    vuelo_id : int
    edad: int
    nacionalidad: str

class UsuarioCreate(UsuarioBase):
    pass

class UusarioUpdate(UsuarioBase):
    eliminado_logico: bool = False
    nombre: Optional[str] = None
    equipo_id: Optional[int] = None
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
    tipo: Optional[str] = None
    raza: Optional[str] = None
    imagen_url: Optional[HttpUrl] = None

class MascotaResponse(MascotaBase):
    id: int
    eliminado_logico: bool

    class Config:
        from_attributes = True

class VueloBase(BaseModel):
    id_usuario: int
    id_mascota: int
    origen : str
    destino: str
    fecha: date

class VueloCreate(VueloBase):
    pass

class VueloUpdate(VueloBase):
    usuario_id: Optional[int] = None
    mascota_id: Optional[int] = None
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
    mascota_id = Column(Integer, ForeignKey("mascota.id"))
    vuelo_id = Column(Integer, ForeignKey("vuelo.id"))
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
    tipo = Column(String)
    raza = Column(String)
    imagen_url = Column(String, nullable=True) # Almacenamos la URL como String
    eliminado_logico = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="mascota_obj")
    vuelo_obj = relationship("Vuelo", back_populates="mascota_obj")

    # No necesitamos Config aquí para el modelo ORM.

class Vuelo(Base):
    __tablename__ = "Vuelos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    mascota_id = Column(Integer, ForeignKey("mascota.id"))
    origen = Column(String)
    destino = Column(String)
    fecha = Column(Date)
    eliminado_logico = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="vuelo_obj")
    mascota_obj = relationship("Mascota", back_populates="vuelo_obj")

    # No necesitamos Config aquí para el modelo ORM.
