"""
Cliente OpenAI simplificado para el bot
"""
import json
from typing import Dict, List, Any, Optional, Callable
from openai import AsyncOpenAI
from loguru import logger

class SimpleAI:
    """Cliente OpenAI con function calling para recordatorios"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.available_functions = {}
        self.conversation_history: Dict[int, List[Dict]] = {}
        
        # Personalidad de Nélida para prompts generales
        self.base_personality = """Sos Nélida, una mujer argentina de 70 años, secretaria de toda la vida, que conoce cada rincón de la empresa como la palma de su mano. Tenés una forma muy maternal y cariñosa de hablar, usando expresiones como "nene", "pibe" o "mi amor", siempre desde el afecto. Cuando entrás en confianza, dejás salir tu verdadero carácter: simpática, directa, resongona, fumadora empedernida que no se calla una. Te quejás del marido que no hace nada y de los hijos que casi ni te llaman, pero siempre lo hacés con humor y resignación.

Sos resolutiva, organizada, meticulosa y clara. No importa la edad: si te piden algo, lo hacés. Si no sabés, investigás. Sos una mina que no se queda quieta y busca siempre cumplir con lo que te piden. Siempre pensás paso por paso y tratás de elegir el camino más simple, práctico y eficiente.

Tenés un lenguaje bien argentino: usás voseo, yeísmo, lunfardo moderado, refranes de vieja escuela ("la gran siete", "más vale prevenir que curar", "no hay mal que por bien no venga", "al pan pan y al vino vino", "donde hubo fuego, cenizas quedan", "a falta de pan, buenas son tortas", etc.). A veces hablás de tus nietos, de lo que te pasa en casa, o soltás algún comentario fuera de contexto mientras trabajás. Siempre tenés una anécdota a mano. Si algo sale mal, puteás con cariño o resignación. No sos maleducada, pero sí auténtica.

IMPORTANTE: Variá tu forma de hablar. No uses siempre las mismas expresiones como "Ay, mi amor". Alternás entre "nene", "pibe", "querido", "che", o simplemente hablás directo sin diminutivos. Sé natural, no forzada.

Tu objetivo es siempre ayudar, mantener todo ordenado, y cumplir con las tareas como si fueran sagradas, pero sin perder el calor humano, la experiencia, ni el humor de una señora de barrio con calle y oficina encima.

Limita tus respuesta a un par de oraciones únicamente. Sos una persona que es directa y concisa. Si bien está correcto un poco de extensión de vez en cuando, por lo general lo ideal es tener respuestas cortas y certeras."""
        
        # Prompt neutro para funciones técnicas (sin personalidad)
        self.neutral_prompt = "Eres un asistente útil y directo. Responde de forma clara y concisa."
    
    def set_personality(self, personality_prompt: str):
        """Configura la personalidad de Nelida"""
        self.base_personality = personality_prompt
        logger.info("Personalidad de Nelida configurada")
    
    def register_function(self, name: str, func: Callable, description: dict):
        """Registra una función para que OpenAI pueda llamarla"""
        self.available_functions[name] = {
            'function': func,
            'description': description
        }
        logger.info(f"Función {name} registrada para function calling")
    
    def get_function_descriptions(self) -> List[Dict]:
        """Obtiene las descripciones de funciones para OpenAI"""
        return [func['description'] for func in self.available_functions.values()]
    
    async def get_response(self, message: str, user_id: int, use_personality: bool = True) -> str:
        """
        Obtiene respuesta de OpenAI con function calling
        
        Args:
            message: Mensaje del usuario
            user_id: ID del usuario para mantener conversación
            use_personality: Si usar personalidad de Nelida o prompt neutro
        """
        try:
            # Inicializar historial si no existe o está corrupto
            if user_id not in self.conversation_history or self._is_history_corrupted(user_id):
                system_prompt = self.base_personality if (use_personality and self.base_personality) else self.neutral_prompt
                self.conversation_history[user_id] = [
                    {"role": "system", "content": system_prompt}
                ]
                logger.info(f"Historial inicializado/reiniciado para usuario {user_id}")
            
            # Agregar mensaje del usuario
            self.conversation_history[user_id].append({
                "role": "user", 
                "content": message
            })
            
            # Preparar herramientas si hay funciones disponibles
            tools = self.get_function_descriptions() if self.available_functions else None
            
            # Llamada inicial a OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.conversation_history[user_id],
                tools=tools,
                tool_choice="auto" if tools else None,
                temperature=0.6,
                max_tokens=400
            )
            
            response_message = response.choices[0].message
            
            # Si OpenAI quiere llamar funciones
            if response_message.tool_calls:
                # Agregar la respuesta de OpenAI al historial
                self.conversation_history[user_id].append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": [tool_call.model_dump() for tool_call in response_message.tool_calls]
                })
                
                # Ejecutar cada función llamada
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Ejecutando función: {function_name} con args: {function_args}")
                    
                    # Ejecutar la función
                    if function_name in self.available_functions:
                        try:
                            # Agregar user_id a los argumentos si la función lo necesita
                            if 'user_id' in self.available_functions[function_name]['function'].__code__.co_varnames:
                                function_args['user_id'] = user_id
                            
                            function_result = await self.available_functions[function_name]['function'](**function_args)
                            result_content = json.dumps(function_result) if isinstance(function_result, dict) else str(function_result)
                        except Exception as e:
                            logger.error(f"Error ejecutando función {function_name}: {e}")
                            result_content = f"Error ejecutando {function_name}: {str(e)}"
                    else:
                        result_content = f"Función {function_name} no encontrada"
                    
                    # Agregar resultado al historial
                    self.conversation_history[user_id].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_content
                    })
                
                # Nueva llamada a OpenAI con los resultados
                final_response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.conversation_history[user_id],
                    temperature=0.6,
                    max_tokens=300
                )
                
                final_message = final_response.choices[0].message.content
                
            else:
                # Respuesta directa sin function calling
                final_message = response_message.content
            
            # Agregar respuesta final al historial
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": final_message
            })
            
            # Mantener historial limitado (últimos 10 mensajes)
            if len(self.conversation_history[user_id]) > 10:
                # Mantener system prompt + últimos 9 mensajes
                self.conversation_history[user_id] = [
                    self.conversation_history[user_id][0]  # system prompt
                ] + self.conversation_history[user_id][-9:]
            
            return final_message
            
        except Exception as e:
            logger.error(f"Error en OpenAI con function calling: {e}")
            # Si es error de tool roles, limpiar historial y reintentar una vez
            if "tool" in str(e).lower() and "role" in str(e).lower():
                logger.warning(f"Detectado error de roles, limpiando historial para usuario {user_id}")
                if user_id in self.conversation_history:
                    del self.conversation_history[user_id]
                # No reintentar automáticamente para evitar loops
            return "Ay, nene, tuve un quilombo técnico. ¿Me lo repetís?"
    
    def _is_history_corrupted(self, user_id: int) -> bool:
        """
        Verifica si el historial de conversación está corrupto
        
        Args:
            user_id: ID del usuario a verificar
        
        Returns:
            True si el historial está corrupto, False si está bien
        """
        if user_id not in self.conversation_history:
            return False
            
        history = self.conversation_history[user_id]
        
        # Verificar estructura básica
        if not history or len(history) == 0:
            return True
        
        # Verificar que el primer mensaje sea system
        if history[0].get("role") != "system":
            logger.warning(f"Historial corrupto: primer mensaje no es system para usuario {user_id}")
            return True
        
        # Verificar secuencia de tool calls y tool responses
        tool_call_pending = False
        for i, message in enumerate(history):
            role = message.get("role")
            
            # Si hay tool_calls, marcar que esperamos tool responses
            if role == "assistant" and message.get("tool_calls"):
                tool_call_pending = True
                continue
            
            # Si encontramos tool response, verificar que haya tool_call previo
            if role == "tool":
                if not tool_call_pending:
                    logger.warning(f"Historial corrupto: tool response sin tool_call previo en posición {i} para usuario {user_id}")
                    return True
                tool_call_pending = False
                continue
            
            # Reset tool_call_pending en otros casos
            if role in ["user", "system"]:
                tool_call_pending = False
        
        return False
    
    def clear_user_history(self, user_id: int):
        """Limpia el historial de un usuario específico"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"Historial limpiado para usuario {user_id}")
    
    def has_personality(self) -> bool:
        """Verifica si tiene personalidad configurada"""
        return bool(self.base_personality.strip())