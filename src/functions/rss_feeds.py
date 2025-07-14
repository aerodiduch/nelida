"""
Sistema RSS para noticias argentinas
Feeds de medios locales para noticias actualizadas en tiempo real
"""
import feedparser
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pytz
from loguru import logger

from ..utils.bot_logger import bot_logger

class RSSManager:
    """Manager para feeds RSS de medios argentinos"""
    
    def __init__(self):
        # Configurar timezone argentino
        self.tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        
        # URLs de feeds RSS de medios argentinos (sin Página 12)
        self.feeds = {
            "clarin": {
                "url": "https://www.clarin.com/rss/lo-ultimo/",
                "nombre": "Clarín",
                "descripcion": "Principal diario argentino"
            },
            "lanacion": {
                "url": "https://servicios.lanacion.com.ar/herramientas/rss/ayuda",
                "nombre": "La Nación", 
                "descripcion": "Diario tradicional argentino"
            },
            "infobae": {
                "url": "https://www.infobae.com/argentina-footer/infobae/rss/",
                "nombre": "Infobae",
                "descripcion": "Portal de noticias digital"
            },
            "perfil": {
                "url": "https://www.perfil.com/feed",
                "nombre": "Perfil",
                "descripcion": "Revista de actualidad"
            },
            "perfil_politica": {
                "url": "https://www.perfil.com/feed/politica", 
                "nombre": "Perfil Política",
                "descripcion": "Noticias políticas"
            },
            "perfil_economia": {
                "url": "https://www.perfil.com/feed/economia",
                "nombre": "Perfil Economía", 
                "descripcion": "Noticias económicas"
            }
        }
        
        logger.info(f"RSSManager inicializado con {len(self.feeds)} feeds argentinos")
    
    def parse_feed(self, feed_key: str) -> List[Dict[str, Any]]:
        """
        Parsear un feed RSS específico
        
        Args:
            feed_key: Clave del feed en self.feeds
            
        Returns:
            Lista de noticias parseadas
        """
        if feed_key not in self.feeds:
            logger.error(f"Feed '{feed_key}' no encontrado")
            return []
        
        feed_info = self.feeds[feed_key]
        
        try:
            # Parsear feed RSS
            feed = feedparser.parse(feed_info["url"])
            
            if feed.bozo:
                logger.warning(f"Feed RSS '{feed_key}' tiene formato irregular")
            
            noticias = []
            
            for entry in feed.entries[:15]:  # Limitar a 15 noticias más recientes
                # Parsear fecha de publicación
                fecha_pub = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    fecha_pub = datetime(*entry.published_parsed[:6])
                    # Convertir a timezone argentino
                    fecha_pub = fecha_pub.replace(tzinfo=pytz.UTC).astimezone(self.tz_argentina)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    fecha_pub = datetime(*entry.updated_parsed[:6])
                    fecha_pub = fecha_pub.replace(tzinfo=pytz.UTC).astimezone(self.tz_argentina)
                
                # Extraer datos de la noticia
                noticia = {
                    "titulo": entry.get('title', 'Sin título'),
                    "descripcion": entry.get('summary', entry.get('description', '')),
                    "link": entry.get('link', ''),
                    "fuente": feed_info["nombre"],
                    "feed_key": feed_key,
                    "fecha_publicacion": fecha_pub,
                    "categoria": self._extraer_categoria(feed_key, entry),
                    "autor": entry.get('author', '')
                }
                
                # Limpiar descripciones HTML
                if noticia["descripcion"]:
                    noticia["descripcion"] = self._limpiar_html(noticia["descripcion"])
                
                noticias.append(noticia)
            
            logger.info(f"Feed '{feed_key}' procesado: {len(noticias)} noticias")
            return noticias
            
        except Exception as e:
            logger.error(f"Error parseando feed '{feed_key}': {e}")
            return []
    
    def obtener_noticias_recientes(self, horas_atras: int = 24) -> List[Dict[str, Any]]:
        """
        Obtener noticias de las últimas X horas de todos los feeds
        
        Args:
            horas_atras: Cuántas horas hacia atrás buscar
            
        Returns:
            Lista de noticias recientes ordenadas por fecha
        """
        ahora = datetime.now(self.tz_argentina)
        limite_tiempo = ahora - timedelta(hours=horas_atras)
        
        todas_noticias = []
        
        # Obtener noticias de todos los feeds
        for feed_key in self.feeds.keys():
            noticias_feed = self.parse_feed(feed_key)
            
            # Filtrar por fecha
            for noticia in noticias_feed:
                if noticia["fecha_publicacion"] and noticia["fecha_publicacion"] >= limite_tiempo:
                    todas_noticias.append(noticia)
        
        # Ordenar por fecha (más reciente primero)
        todas_noticias.sort(
            key=lambda x: x["fecha_publicacion"] if x["fecha_publicacion"] else datetime.min.replace(tzinfo=self.tz_argentina),
            reverse=True
        )
        
        logger.info(f"Encontradas {len(todas_noticias)} noticias de las últimas {horas_atras} horas")
        return todas_noticias
    
    def obtener_noticias_por_categoria(self, categoria: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener noticias de una categoría específica
        
        Args:
            categoria: política, economía, deportes, etc.
            limite: Máximo número de noticias
            
        Returns:
            Lista de noticias de la categoría
        """
        todas_noticias = self.obtener_noticias_recientes(48)  # Últimas 48 horas
        
        categoria_lower = categoria.lower()
        noticias_categoria = []
        
        for noticia in todas_noticias:
            if (categoria_lower in noticia["categoria"].lower() or 
                categoria_lower in noticia["titulo"].lower() or
                categoria_lower in noticia["descripcion"].lower()):
                noticias_categoria.append(noticia)
                
                if len(noticias_categoria) >= limite:
                    break
        
        logger.info(f"Encontradas {len(noticias_categoria)} noticias de categoría '{categoria}'")
        return noticias_categoria
    
    def obtener_noticias_por_fuente(self, fuente: str, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Obtener noticias de una fuente específica
        
        Args:
            fuente: clarín, lanacion, infobae, perfil
            limite: Máximo número de noticias
            
        Returns:
            Lista de noticias de la fuente
        """
        fuente_key = fuente.lower().replace(" ", "").replace("ñ", "n")
        
        # Mapear nombres comunes a keys
        mapeo_fuentes = {
            "clarin": "clarin",
            "lanacion": "lanacion", 
            "nacion": "lanacion",
            "infobae": "infobae",
            "perfil": "perfil"
        }
        
        feed_key = mapeo_fuentes.get(fuente_key)
        if not feed_key:
            logger.warning(f"Fuente '{fuente}' no reconocida")
            return []
        
        noticias = self.parse_feed(feed_key)
        return noticias[:limite]
    
    def _extraer_categoria(self, feed_key: str, entry) -> str:
        """Extraer categoría de la noticia basada en el feed y contenido"""
        # Categorías basadas en el feed
        if "politica" in feed_key:
            return "Política"
        elif "economia" in feed_key:
            return "Economía"
        elif "deportes" in feed_key:
            return "Deportes"
        
        # Detectar categoría por palabras clave en título/descripción
        texto = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        
        if any(palabra in texto for palabra in ["milei", "gobierno", "congreso", "senado", "política", "elecciones"]):
            return "Política"
        elif any(palabra in texto for palabra in ["dólar", "inflación", "economía", "peso", "mercado", "banco"]):
            return "Economía"
        elif any(palabra in texto for palabra in ["boca", "river", "fútbol", "messi", "deportes", "racing"]):
            return "Deportes"
        elif any(palabra in texto for palabra in ["internacional", "mundo", "estados unidos", "europa"]):
            return "Internacional"
        else:
            return "General"
    
    def _limpiar_html(self, texto: str) -> str:
        """Limpiar tags HTML de la descripción"""
        import re
        # Remover tags HTML básicos
        texto = re.sub(r'<[^>]+>', '', texto)
        # Limpiar entidades HTML comunes
        texto = texto.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        texto = texto.replace('&quot;', '"').replace('&#39;', "'")
        # Limpiar espacios extra
        texto = ' '.join(texto.split())
        return texto.strip()

# Instancia global del manager RSS
rss_manager = RSSManager()

async def obtener_noticias_hoy(limite: int = 8, user_id: int = None) -> Dict[str, Any]:
    """
    Obtener las noticias más importantes de hoy de medios argentinos
    
    Args:
        limite: Número máximo de noticias (default 8)
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        noticias = rss_manager.obtener_noticias_recientes(24)  # Últimas 24 horas
        
        if not noticias:
            return {
                "success": False,
                "error": "No se encontraron noticias recientes"
            }
        
        # Limitar cantidad
        noticias_limitadas = noticias[:limite]
        
        # Formatear para respuesta
        noticias_formateadas = []
        for noticia in noticias_limitadas:
            fecha_str = ""
            if noticia["fecha_publicacion"]:
                fecha_str = noticia["fecha_publicacion"].strftime("%H:%M")
            
            noticias_formateadas.append({
                "titulo": noticia["titulo"],
                "descripcion": noticia["descripcion"][:200] + "..." if len(noticia["descripcion"]) > 200 else noticia["descripcion"],
                "fuente": noticia["fuente"],
                "categoria": noticia["categoria"],
                "hora": fecha_str,
                "link": noticia["link"]
            })
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_noticias_hoy",
            success=True, details=f"{len(noticias_formateadas)} noticias encontradas"
        )
        
        return {
            "success": True,
            "noticias": noticias_formateadas,
            "total": len(noticias_formateadas),
            "fuentes": list(set([n["fuente"] for n in noticias_formateadas]))
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error obteniendo noticias de hoy: {error_msg}")
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_noticias_hoy",
            success=False, error=error_msg
        )
        
        return {
            "success": False,
            "error": f"Error obteniendo noticias: {error_msg}"
        }

async def obtener_noticias_categoria(categoria: str, limite: int = 5, user_id: int = None) -> Dict[str, Any]:
    """
    Obtener noticias de una categoría específica
    
    Args:
        categoria: política, economía, deportes, internacional, etc.
        limite: Número máximo de noticias (default 5)
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        noticias = rss_manager.obtener_noticias_por_categoria(categoria, limite)
        
        if not noticias:
            return {
                "success": False,
                "error": f"No se encontraron noticias de {categoria}"
            }
        
        # Formatear para respuesta
        noticias_formateadas = []
        for noticia in noticias:
            fecha_str = ""
            if noticia["fecha_publicacion"]:
                fecha_str = noticia["fecha_publicacion"].strftime("%H:%M")
            
            noticias_formateadas.append({
                "titulo": noticia["titulo"],
                "descripcion": noticia["descripcion"][:150] + "..." if len(noticia["descripcion"]) > 150 else noticia["descripcion"],
                "fuente": noticia["fuente"],
                "hora": fecha_str
            })
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_noticias_categoria",
            success=True, details=f"Categoría: {categoria}, {len(noticias_formateadas)} noticias"
        )
        
        return {
            "success": True,
            "categoria": categoria,
            "noticias": noticias_formateadas,
            "total": len(noticias_formateadas)
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error obteniendo noticias de categoría {categoria}: {error_msg}")
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_noticias_categoria",
            success=False, error=error_msg
        )
        
        return {
            "success": False,
            "error": f"Error obteniendo noticias de {categoria}: {error_msg}"
        }

# Definiciones para OpenAI Function Calling
RSS_FUNCTIONS = {
    "obtener_noticias_hoy": {
        "type": "function",
        "function": {
            "name": "obtener_noticias_hoy",
            "description": "Obtener las noticias más importantes de hoy de medios argentinos (Clarín, La Nación, Infobae, Perfil). Usar cuando el usuario pida 'noticias de hoy', 'qué pasó hoy', 'noticias importantes', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limite": {
                        "type": "integer",
                        "description": "Número máximo de noticias a mostrar (entre 3 y 15)",
                        "default": 8,
                        "minimum": 3,
                        "maximum": 15
                    }
                },
                "required": []
            }
        }
    },
    
    "obtener_noticias_categoria": {
        "type": "function",
        "function": {
            "name": "obtener_noticias_categoria",
            "description": "Obtener noticias de una categoría específica (política, economía, deportes, internacional). Usar cuando el usuario pida noticias de un tema particular.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Categoría de noticias: 'política', 'economía', 'deportes', 'internacional', 'general'"
                    },
                    "limite": {
                        "type": "integer",
                        "description": "Número máximo de noticias (entre 3 y 10)",
                        "default": 5,
                        "minimum": 3,
                        "maximum": 10
                    }
                },
                "required": ["categoria"]
            }
        }
    }
}