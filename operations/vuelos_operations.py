from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_ # ¡Correcto! Ya estaba importado, lo mantenemos.
from sqlalchemy.exc import IntegrityError, OperationalError
from data import models
from data.models import VueloCreate, VueloUpdate
from datetime import date
from typing import Optional

# --- Operaciones CRUD para vuelos ---

def create_vuelo(db: Session, vuelo: VueloCreate):
    try:
        usuario_existente = db.query(models.Usuario).filter(models.usuario.id == mascota.usuario_id).first()
        if not usuario_existente:
            raise ValueError(
                f"¡Atención! El vuelo con ID {vuelo.usuario_id} no existe. No se puede crear la reserva.")

        db_vuelo = models.Vuelo(
            origen=vuelo.origen,
            destino=vuelo.destino,
            fecha=vuelo.fecha,
        )
        db.add(db_vuelo)
        db.commit()
        db.refresh(db_vuelo)
        return db_vuelo
    except ValueError as e:
        db.rollback()
        print(f"Error al crear reserva: {e}")
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al añadir reserva! Detalles: {e}")
        raise ValueError("No se pudo añadir la reserva. Asegúrate de que el id_usuario sea válido.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al crear reserva: {e}")
        raise

def get_all_vuelos(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Vuelo).options(joinedload(models.Vuelo.Usuario)).filter(
            models.Vuelo.eliminado_logico == False
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener reservas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al obtener todas las reservas! Detalles: {e}")
        raise

def get_vuelo_by_id(db: Session, id_vuelo: int):
    try:
        return db.query(models.Vuelo).options(joinedload(models.Vuelo.Usuario)).filter(
            models.Vuelo.id == id_vuelo
        ).first()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar vuelo por ID! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"¡Error desconocido al buscar vuelo por ID {equipo_id}! Detalles: {e}")
        raise

def update_vuelo(db: Session, id_vuelo: int, vuelo: VueloUpdate):
    try:
        db_vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == id_vuelo).first()
        if db_vuelo:
            update_data = vuelo.model_dump(exclude_unset=True)
            if 'usuario_id' in update_data and update_data['usaurio_id'] is not None:
                usuario_existente = db.query(models.Vuelo).filter(models.Vuelo.id == update_data['usuario_id']).first()
                if not usuario_existente:
                    raise ValueError(f"¡Atención! El usuario con ID {update_data['usuario_id']} no existe. No se puede actualizar la reserva.")

            for key, value in update_data.items():
                setattr(db_vuelo, key, value)
            db.commit()
            db.refresh(db_vuelo)
        return db_vuelo
    except ValueError as e:
        db.rollback()
        print(f"Error al actualizar reserva: {e}")
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"¡Error de integridad al actualizar la reserva! Detalles: {e}")
        raise ValueError("No se pudo actualizar la reserva debido a datos inválidos o duplicados.")
    except Exception as e:
        db.rollback()
        print(f"¡Oops! Un error inesperado ocurrió al actualizar la reserva con ID {id_vuelo}: {e}")
        raise

def soft_delete_vuelo(db: Session, id_vuelo: int):
    try:
        db_vuelo = db.query(models.Mascota).filter(models.Mascota.id == mascota_id).first()
        if db_vuelo:
            db_vuelo.eliminado_logico = True
            db.commit()
            db.refresh(db_vuelo)
        return db_vuelo
    except OperationalError as e:
        db.rollback()
        print(f"¡Problema de conexión con la base de datos al eliminar reserva {id_vuelo}! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para eliminar la reserva.")
    except Exception as e:
        db.rollback()
        print(f"¡Error desconocido al intentar eliminar lógicamente la reserva con ID {id_vuelo}! Detalles: {e}")
        raise

def search_vuelos(
    db: Session,
    query_str: Optional[str] = None, # Renombrado para evitar conflicto con 'query' de SQLAlchemy
    id_usuario: Optional[int] = None,
    origen : Optional[str] = None,
    destino: Optional[str] = None,
    fecha: Optional[date] = None,
    id_vuelo: Optional[int] = None, # Renombrado para mayor claridad
    eliminado: bool = False
):

    try:
        base_query = db.query(models.Vuelo).options(joinedload(models.Vuelo.usuario_obj)).filter(
            models.Vuelo.eliminado_logico == eliminado
        )

        filters = []

        if query_str:
            filters.append(
                or_(
                    models.Vuelo.nombre.ilike(f"%{query_str}%"),
                    models.Vuelo.usuario_obj.has(models.Usuario.nombre.ilike(f"%{query_str}%"))
                )
            )
        if usuario_id:
            filters.append(models.Mascota.usuario_id == id_usuario)
        if origen:
            filters.append(models.Vuelo.origen.ilike(f"%{origen}%"))
        if destino:
            filters.append(models.Vuelo.destino.ilike(f"%{destino}%"))
        if fecha:
            filters.append(models.Vuelo.fecha.ilike(f"%{fecha}%"))
        if id_vuelo:
            filters.append(models.Vuelo.id == id_vuelo)

        # Aplica todos los filtros
        if filters:
            base_query = base_query.filter(*filters)

        return base_query.all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al buscar reservas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para la búsqueda de reservas.")
    except Exception as e:
        print(f"¡Error desconocido al buscar reservas! Detalles: {e}")
        raise


def get_soft_deleted_vuelos(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Vuelo).filter(
            models.Vuelo.eliminado_logico == True
        ).offset(skip).limit(limit).all()
    except OperationalError as e:
        print(f"¡Problema de conexión con la base de datos al obtener reservas eliminadas! Detalles: {e}")
        raise ConnectionError("No se pudo conectar a la base de datos para obtener reservas eliminados.")
    except Exception as e:
        print(f"¡Error desconocido al obtener reservas eliminadas lógicamente! Detalles: {e}")
        raise