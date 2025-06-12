from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_ #
from sqlalchemy.exc import IntegrityError, OperationalError
from data import models
from data.models import MascotaCreate, MascotaUpdate
from typing import Optional

# --- Operaciones CRUD para mascotas ---

def create_mascota(db: Session, mascota: MascotaCreate):
    try:
        usuario_existente = db.query(models.Usuario).filter(models.usuario.id == mascota.usuario_id).first()
        if not usuario_existente:
            raise ValueError(
                f"¡Atención! La mascota con ID {mascota.usuario_id} no existe. No se puede crear la mascota.")

        db_mascota = models.Mascota(
            nombre=mascota.nombre,
            pais=mascota.pais,
            grupo=mascota.grupo,
            imagen_url=imagen_url_str
        )
        db.add(db_mascota)
        db.commit()
        db.refresh(db_mascota)
        return db_mascota
    except ValueError as e:
        db.rollback()
        print(f"Error al crear mascota: {e}")
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al añadir a la mascota! Detalles: {e}")
        raise ValueError("No se pudo añadir a la mascota. Asegúrate de que el usaurio_id sea válido.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al crear ella mascota: {e}")
        raise

def get_all_mascotas(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Mascota).options(joinedload(models.Mascota.Usuario)).filter(
            models.Mascota.eliminado_logico == False
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener mascotas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al obtener todas las mascotas! Detalles: {e}")
        raise

def get_mascota_by_id(db: Session, mascota_id: int):
    try:
        return db.query(models.Mascota).options(joinedload(models.Mascota.Usuario)).filter(
            models.Mascota.id == mascota_id
        ).first()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar mascota por ID! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al buscar mascota por ID {equipo_id}! Detalles: {e}")
        raise

def update_mascota(db: Session, mascota_id: int, mascota: MascotaUpdate):
    try:
        db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
        if db_mascota:
            update_data = mascota.model_dump(exclude_unset=True)
            if 'usuario_id' in update_data and update_data['usaurio_id'] is not None:
                usuario_existente = db.query(models.Vuelo).filter(models.Vuelo.id == update_data['usuario_id']).first()
                if not usuario_existente:
                    raise ValueError(f"¡Atención! El usuario con ID {update_data['usuario_id']} no existe. No se puede actualizar la mascota.")

            for key, value in update_data.items():
                setattr(db_mascota, key, value)
            db.commit()
            db.refresh(db_mascota)
        return db_mascota
    except ValueError as e:
        db.rollback()
        print(f"Error al actualizar mascota: {e}")
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al actualizar la mascota! Detalles: {e}")
        raise ValueError("No se pudo actualizar la mascota debido a datos inválidos o duplicados.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al actualizar la mascota con ID {mascota_id}: {e}")
        raise

def soft_delete_mascota(db: Session, mascota_id: int):
    try:
        db_mascota = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
        if db_mascota:
            db_mascota.eliminado_logico = True
            db.commit()
            db.refresh(db_mascota)
        return db_mascota
    except OperationalError as e:
        db.rollback()
        print(f"¡Problema de conexión con la base de datos al eliminar mascota {mascota_id}! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para eliminar la mascota.")
    except Exception as e:
        db.rollback()
        print(f"¡Error desconocido al intentar eliminar lógicamente la mascota con ID {equipo_id}! Detalles: {e}")
        raise

def search_mascotas(
    db: Session,
    query_str: Optional[str] = None, # Renombrado para evitar conflicto con 'query' de SQLAlchemy
    id_usuario: Optional[int] = None,
    nombre: Optional[str] = None,
    tipo: Optional[str] = None,
    raza: Optional[str] = None,
    id_mascota: Optional[int] = None, # Renombrado para mayor claridad
    eliminado: bool = False
):

    try:
        base_query = db.query(models.Mascota).options(joinedload(models.Mascota.usuario_obj)).filter(
            models.Mascota.eliminado_logico == eliminado
        )

        filters = []

        if query_str:
            filters.append(
                or_(
                    models.Mascota.nombre.ilike(f"%{query_str}%"),
                    models.Mascota.usuario_obj.has(models.Usuario.nombre.ilike(f"%{query_str}%"))
                )
            )
        if usuario_id:
            filters.append(models.Mascota.usuario_id == id_usuario)
        if nombre:
            filters.append(models.Mascota.nombre.ilike(f"%{nombre}%"))
        if tipo:
            filters.append(models.Mascota.tipo.ilike(f"%{Tipo}%"))
        if raza:
            filters.append(models.Mascota.raza.ilike(f"%{raza}%"))
        if id_mascota:
            filters.append(models.Mascota.id == id_mascota)

        # Aplica todos los filtros
        if filters:
            base_query = base_query.filter(*filters)

        return base_query.all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar mascotas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para la búsqueda de mascotas.")
    except Exception as e:
        print(f"¡Error desconocido al buscar mascotas! Detalles: {e}")
        raise


def get_soft_deleted_mascotas(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Mascota).filter(
            models.Mascota.eliminado_logico == True
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener mascotas eliminadas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para obtener mascotas eliminadas.")
    except Exception as e:
        print(f"¡Error desconocido al obtener mascotas eliminadas lógicamente! Detalles: {e}")
        raise