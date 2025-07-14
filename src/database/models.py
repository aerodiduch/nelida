"""
Modelos de base de datos para Nelida Assistant
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

class Database:
    """Manejo de la base de datos SQLite"""
    
    def __init__(self, db_path: str = "data/nelida.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Crear directorio data si no existe"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Directorio {data_dir} creado")
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        return conn
    
    def init_database(self):
        """Inicializar tablas de la base de datos"""
        with self.get_connection() as conn:
            # Tabla de recordatorios
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recordatorios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    fecha_recordatorio DATETIME NOT NULL,
                    prioridad TEXT DEFAULT 'media' CHECK (prioridad IN ('alta', 'media', 'baja')),
                    status TEXT DEFAULT 'pendiente' CHECK (status IN ('pendiente', 'completado', 'cancelado')),
                    user_id INTEGER NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para mejorar performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recordatorios_user_id 
                ON recordatorios(user_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recordatorios_fecha 
                ON recordatorios(fecha_recordatorio)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recordatorios_status 
                ON recordatorios(status)
            """)
            
            # Tabla de tareas (para TO-DOs sin fecha específica)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tareas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    prioridad TEXT DEFAULT 'media' CHECK (prioridad IN ('alta', 'media', 'baja')),
                    status TEXT DEFAULT 'pendiente' CHECK (status IN ('pendiente', 'completado', 'cancelado')),
                    categoria TEXT DEFAULT 'general',
                    user_id INTEGER NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para tareas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tareas_user_id 
                ON tareas(user_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tareas_status 
                ON tareas(status)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tareas_categoria 
                ON tareas(categoria)
            """)
            
            # Tabla de notas (para anotaciones sueltas)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    categoria TEXT DEFAULT 'general',
                    user_id INTEGER NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para notas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_notas_user_id 
                ON notas(user_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_notas_categoria 
                ON notas(categoria)
            """)
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente")

class Recordatorio:
    """Modelo para manejar recordatorios"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def crear(self, contenido: str, fecha_recordatorio: datetime, user_id: int, 
              prioridad: str = 'media') -> int:
        """
        Crear un nuevo recordatorio
        
        Args:
            contenido: Texto del recordatorio
            fecha_recordatorio: Cuándo debe recordarse
            user_id: ID del usuario de Telegram
            prioridad: alta, media, baja
            
        Returns:
            ID del recordatorio creado
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO recordatorios 
                (contenido, fecha_recordatorio, prioridad, user_id)
                VALUES (?, ?, ?, ?)
            """, (contenido, fecha_recordatorio, prioridad, user_id))
            
            recordatorio_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Recordatorio creado - ID: {recordatorio_id}, Usuario: {user_id}")
            return recordatorio_id
    
    def obtener_por_id(self, recordatorio_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un recordatorio por ID"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM recordatorios WHERE id = ?
            """, (recordatorio_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def listar_por_usuario(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Listar recordatorios de un usuario
        
        Args:
            user_id: ID del usuario
            status: Filtrar por status (opcional)
        """
        query = "SELECT * FROM recordatorios WHERE user_id = ?"
        params = [user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY fecha_recordatorio ASC"
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def actualizar_status(self, recordatorio_id: int, nuevo_status: str) -> bool:
        """
        Actualizar el status de un recordatorio
        
        Args:
            recordatorio_id: ID del recordatorio
            nuevo_status: pendiente, completado, cancelado
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE recordatorios 
                SET status = ?, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (nuevo_status, recordatorio_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Recordatorio {recordatorio_id} actualizado a {nuevo_status}")
            else:
                logger.warning(f"No se encontró recordatorio con ID {recordatorio_id}")
            
            return success
    
    def eliminar(self, recordatorio_id: int) -> bool:
        """Eliminar un recordatorio"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM recordatorios WHERE id = ?
            """, (recordatorio_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Recordatorio {recordatorio_id} eliminado")
            else:
                logger.warning(f"No se encontró recordatorio con ID {recordatorio_id}")
            
            return success
    
    def obtener_pendientes_hasta(self, fecha_limite: datetime) -> List[Dict[str, Any]]:
        """Obtener recordatorios pendientes hasta una fecha"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM recordatorios 
                WHERE status = 'pendiente' 
                AND fecha_recordatorio <= ?
                ORDER BY fecha_recordatorio ASC
            """, (fecha_limite,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

class Tarea:
    """Modelo para manejar tareas (TO-DOs sin fecha específica)"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def crear(self, contenido: str, user_id: int, prioridad: str = 'media', 
              categoria: str = 'general') -> int:
        """
        Crear una nueva tarea
        
        Args:
            contenido: Texto de la tarea
            user_id: ID del usuario de Telegram
            prioridad: alta, media, baja
            categoria: categoría para organizar (ej: trabajo, personal, casa)
            
        Returns:
            ID de la tarea creada
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tareas 
                (contenido, prioridad, categoria, user_id)
                VALUES (?, ?, ?, ?)
            """, (contenido, prioridad, categoria, user_id))
            
            tarea_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Tarea creada - ID: {tarea_id}, Usuario: {user_id}")
            return tarea_id
    
    def obtener_por_id(self, tarea_id: int) -> Optional[Dict[str, Any]]:
        """Obtener una tarea por ID"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM tareas WHERE id = ?
            """, (tarea_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def listar_por_usuario(self, user_id: int, status: Optional[str] = None, 
                          categoria: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Listar tareas de un usuario
        
        Args:
            user_id: ID del usuario
            status: Filtrar por status (opcional)
            categoria: Filtrar por categoría (opcional)
        """
        query = "SELECT * FROM tareas WHERE user_id = ?"
        params = [user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
            
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        
        query += " ORDER BY prioridad DESC, fecha_creacion ASC"
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def actualizar_status(self, tarea_id: int, nuevo_status: str) -> bool:
        """
        Actualizar el status de una tarea
        
        Args:
            tarea_id: ID de la tarea
            nuevo_status: pendiente, completado, cancelado
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE tareas 
                SET status = ?, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (nuevo_status, tarea_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                logger.info(f"Tarea {tarea_id} actualizada a {nuevo_status}")
            else:
                logger.warning(f"No se encontró tarea con ID {tarea_id}")
            
            return success
    
    def completar_multiples(self, contenidos_parciales: List[str], user_id: int) -> Dict[str, Any]:
        """
        Marcar múltiples tareas como completadas basándose en contenido parcial
        
        Args:
            contenidos_parciales: Lista de textos que deben aparecer en las tareas
            user_id: ID del usuario
            
        Returns:
            Dict con resultados: completadas, no_encontradas
        """
        completadas = []
        no_encontradas = []
        
        for contenido_parcial in contenidos_parciales:
            # Buscar tareas que contengan el texto (case insensitive)
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM tareas 
                    WHERE user_id = ? 
                    AND status = 'pendiente' 
                    AND LOWER(contenido) LIKE LOWER(?)
                    ORDER BY fecha_creacion ASC
                    LIMIT 1
                """, (user_id, f"%{contenido_parcial}%"))
                
                tarea = cursor.fetchone()
                
                if tarea:
                    # Marcar como completada
                    success = self.actualizar_status(tarea['id'], 'completado')
                    if success:
                        completadas.append({
                            'id': tarea['id'],
                            'contenido': tarea['contenido'],
                            'busqueda': contenido_parcial
                        })
                    else:
                        no_encontradas.append(contenido_parcial)
                else:
                    no_encontradas.append(contenido_parcial)
        
        return {
            'completadas': completadas,
            'no_encontradas': no_encontradas
        }
    
    def buscar_por_contenido(self, texto_busqueda: str, user_id: int) -> List[Dict[str, Any]]:
        """Buscar tareas por contenido (útil para completar múltiples)"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM tareas 
                WHERE user_id = ? 
                AND LOWER(contenido) LIKE LOWER(?)
                ORDER BY fecha_creacion ASC
            """, (user_id, f"%{texto_busqueda}%"))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

class Nota:
    """Modelo para manejar notas/anotaciones"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def crear(self, contenido: str, user_id: int, categoria: str = 'general') -> int:
        """
        Crear una nueva nota
        
        Args:
            contenido: Texto de la nota
            user_id: ID del usuario
            categoria: Categoría de la nota
            
        Returns:
            ID de la nota creada
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO notas (contenido, categoria, user_id)
                VALUES (?, ?, ?)
            """, (contenido, categoria, user_id))
            
            nota_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Nota creada - ID: {nota_id}, Usuario: {user_id}")
            return nota_id
    
    def listar_por_usuario(self, user_id: int, categoria: str = None) -> List[Dict[str, Any]]:
        """
        Listar notas de un usuario
        
        Args:
            user_id: ID del usuario
            categoria: Filtrar por categoría (opcional)
            
        Returns:
            Lista de notas
        """
        with self.db.get_connection() as conn:
            if categoria:
                cursor = conn.execute("""
                    SELECT * FROM notas 
                    WHERE user_id = ? AND categoria = ?
                    ORDER BY fecha_creacion DESC
                """, (user_id, categoria))
            else:
                cursor = conn.execute("""
                    SELECT * FROM notas 
                    WHERE user_id = ?
                    ORDER BY fecha_creacion DESC
                """, (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def buscar_por_contenido(self, texto_busqueda: str, user_id: int) -> List[Dict[str, Any]]:
        """
        Buscar notas por contenido
        
        Args:
            texto_busqueda: Texto a buscar
            user_id: ID del usuario
            
        Returns:
            Lista de notas que coinciden
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM notas 
                WHERE user_id = ? 
                AND LOWER(contenido) LIKE LOWER(?)
                ORDER BY fecha_creacion DESC
            """, (user_id, f"%{texto_busqueda}%"))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def eliminar(self, nota_id: int, user_id: int) -> bool:
        """
        Eliminar una nota
        
        Args:
            nota_id: ID de la nota
            user_id: ID del usuario (para verificar permisos)
            
        Returns:
            True si se eliminó, False si no
        """
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM notas 
                WHERE id = ? AND user_id = ?
            """, (nota_id, user_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Nota eliminada - ID: {nota_id}, Usuario: {user_id}")
                return True
            else:
                logger.warning(f"No se pudo eliminar nota - ID: {nota_id}, Usuario: {user_id}")
                return False

# Instancia global de la base de datos
database = Database()
recordatorio_model = Recordatorio(database)
tarea_model = Tarea(database)
nota_model = Nota(database)