"""
Funciones de búsqueda en internet para function calling con OpenAI
"""
import os
from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
from loguru import logger

from ..utils.bot_logger import bot_logger

class GoogleSearchClient:
    """Cliente para búsquedas con Google Custom Search API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_CX')
        self.service = None
        
        if self.api_key and self.search_engine_id:
            try:
                self.service = build("customsearch", "v1", developerKey=self.api_key)
                logger.info("Google Search API configurado correctamente")
            except Exception as e:
                logger.error(f"Error configurando Google Search API: {e}")
        else:
            logger.warning("Google Search API no configurado - usando búsqueda alternativa")
    
    def is_available(self) -> bool:
        """Verifica si la API está disponible"""
        return self.service is not None
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Buscar en Google usando Custom Search API
        
        Args:
            query: Término de búsqueda
            num_results: Número de resultados (máximo 10)
            
        Returns:
            Lista de resultados con título, link y snippet
        """
        if not self.is_available():
            raise Exception("Google Search API no está configurado")
        
        try:
            # Ejecutar búsqueda
            result = self.service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=min(num_results, 10)  # Google limita a 10 por request
            ).execute()
            
            # Procesar resultados
            search_results = []
            if 'items' in result:
                for item in result['items']:
                    search_results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'displayLink': item.get('displayLink', '')
                    })
            
            logger.info(f"Búsqueda Google exitosa: '{query}' - {len(search_results)} resultados")
            return search_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda Google: {e}")
            raise

class AlternativeSearchClient:
    """Cliente de búsqueda alternativo cuando Google API no está disponible"""
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda alternativa usando scraping básico de DuckDuckGo
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Buscar en DuckDuckGo
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Parsear resultados de DuckDuckGo - selectores actualizados
            result_containers = soup.find_all('div', class_='web-result') or soup.find_all('div', class_='result')
            
            for result_div in result_containers[:num_results]:
                # Intentar múltiples selectores para título y link
                title_elem = (result_div.find('a', class_='result__a') or 
                             result_div.find('h2') and result_div.find('h2').find('a') or
                             result_div.find('a'))
                
                # Buscar snippet en diferentes elementos
                snippet_elem = (result_div.find('a', class_='result__snippet') or
                               result_div.find('span', class_='result__snippet') or
                               result_div.find('div', class_='snippet'))
                
                if title_elem:
                    href = title_elem.get('href', '')
                    title_text = title_elem.get_text(strip=True)
                    snippet_text = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # Si no hay snippet, buscar en párrafos cercanos
                    if not snippet_text:
                        p_elem = result_div.find('p') or result_div.find('div', class_='snippet')
                        if p_elem:
                            snippet_text = p_elem.get_text(strip=True)
                    
                    results.append({
                        'title': title_text,
                        'link': href,
                        'snippet': snippet_text[:200] if snippet_text else 'Sin descripción disponible',
                        'displayLink': href.split('/')[2] if href and '/' in href else ''
                    })
            
            logger.info(f"Búsqueda DuckDuckGo exitosa: '{query}' - {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda alternativa: {e}")
            return []

# Instancia global del cliente de búsqueda
google_client = GoogleSearchClient()
alternative_client = AlternativeSearchClient()

def _should_trigger_search(text: str) -> bool:
    """
    Determina si el texto contiene keywords específicos para búsqueda
    
    Args:
        text: Texto del usuario a analizar
        
    Returns:
        True si contiene keywords de búsqueda, False para texto suelto
    """
    search_keywords = [
        "buscame", "averiguame", "buscar en internet", "googlear",
        "investigá", "consultá", "mirá en google", "qué dice internet",
        "información sobre", "busca información", "busca datos",
        "qué hay sobre", "conseguime información", "investigame"
    ]
    
    text_lower = text.lower().strip()
    
    for keyword in search_keywords:
        if keyword in text_lower:
            return True
    
    return False

async def buscar_en_internet(query: str, num_resultados: int = 5, user_id: int = None) -> Dict[str, Any]:
    """
    Buscar información en internet
    
    Args:
        query: Qué buscar
        num_resultados: Cantidad de resultados (1-10)
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        # Validar parámetros
        if not query or len(query.strip()) < 2:
            return {
                "success": False,
                "error": "La búsqueda debe tener al menos 2 caracteres"
            }
        
        num_resultados = max(1, min(num_resultados, 10))  # Entre 1 y 10
        
        # Intentar con Google API primero
        resultados = []
        metodo_usado = ""
        
        if google_client.is_available():
            try:
                resultados = google_client.search(query, num_resultados)
                metodo_usado = "Google Custom Search API"
            except Exception as e:
                logger.warning(f"Google API falló, usando alternativa: {e}")
                resultados = alternative_client.search(query, num_resultados)
                metodo_usado = "DuckDuckGo (alternativo)"
        else:
            resultados = alternative_client.search(query, num_resultados)
            metodo_usado = "DuckDuckGo (alternativo)"
        
        # Log de la búsqueda
        bot_logger.log_function_call(
            user_id, "usuario", "buscar_internet",
            success=True, 
            details=f"Query: '{query}', Resultados: {len(resultados)}, Método: {metodo_usado}"
        )
        
        return {
            "success": True,
            "query": query,
            "resultados": resultados,
            "total": len(resultados),
            "metodo": metodo_usado
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error en búsqueda: {error_msg}")
        
        bot_logger.log_function_call(
            user_id, "usuario", "buscar_internet",
            success=False, error=error_msg
        )
        
        return {
            "success": False,
            "error": f"Error realizando búsqueda: {error_msg}"
        }

async def obtener_contenido_pagina(url: str, user_id: int = None) -> Dict[str, Any]:
    """
    Obtener el contenido de una página web específica
    
    Args:
        url: URL de la página a leer
        user_id: ID del usuario (se pasa automáticamente)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer título
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "Sin título"
        
        # Extraer contenido principal (heurística mejorada)
        content_selectors = [
            'article', 'main', '.content', '#content', 
            '.post-content', '.entry-content', '.article-body',
            '.post-body', '[role="main"]', '.container'
        ]
        
        content_text = ""
        
        # Primero intentar con selectores específicos
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remover elementos no deseados antes de extraer texto
                for unwanted in content_elem(["script", "style", "nav", "header", "footer", "aside"]):
                    unwanted.decompose()
                text = content_elem.get_text(separator=' ', strip=True)
                if len(text) > 100:  # Solo usar si tiene contenido sustancial
                    content_text = text
                    break
        
        # Si no encontró contenido específico, usar estrategia más agresiva
        if not content_text or len(content_text) < 100:
            body = soup.find('body')
            if body:
                # Remover elementos no deseados
                for unwanted in body(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                    unwanted.decompose()
                
                # Buscar párrafos con contenido
                paragraphs = body.find_all(['p', 'div'], string=True)
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20:  # Solo párrafos con contenido sustancial
                        text_parts.append(text)
                
                if text_parts:
                    content_text = ' '.join(text_parts)
                else:
                    # Último recurso: todo el body
                    content_text = body.get_text(separator=' ', strip=True)
        
        # Limitar texto a 2000 caracteres para no saturar
        if len(content_text) > 2000:
            content_text = content_text[:2000] + "..."
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_contenido_pagina",
            success=True, details=f"URL: {url}, Caracteres: {len(content_text)}"
        )
        
        return {
            "success": True,
            "url": url,
            "title": title_text,
            "content": content_text,
            "length": len(content_text)
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error obteniendo contenido de {url}: {error_msg}")
        
        bot_logger.log_function_call(
            user_id, "usuario", "obtener_contenido_pagina",
            success=False, error=error_msg
        )
        
        return {
            "success": False,
            "error": f"No pude acceder a la página: {error_msg}"
        }

# Definiciones de funciones para OpenAI Function Calling
BUSQUEDA_FUNCTIONS = {
    "buscar_en_internet": {
        "type": "function",
        "function": {
            "name": "buscar_en_internet",
            "description": "Buscar información en internet usando Google. SOLO usar cuando el usuario incluya palabras específicas de búsqueda como: 'buscame', 'averiguame', 'buscar en internet', 'googlear', 'investigá', 'consultá', 'mirá en google', 'qué dice internet sobre', 'información sobre'. NO usar para texto suelto o anotaciones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Términos de búsqueda (ej: 'Python programming', 'noticias Argentina', 'clima Buenos Aires')"
                    },
                    "num_resultados": {
                        "type": "integer",
                        "description": "Cantidad de resultados a mostrar (entre 1 y 10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    "obtener_contenido_pagina": {
        "type": "function",
        "function": {
            "name": "obtener_contenido_pagina",
            "description": "Leer el contenido completo de una página web específica. Usar cuando el usuario quiera leer una página en particular.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL completa de la página web a leer"
                    }
                },
                "required": ["url"]
            }
        }
    }
}