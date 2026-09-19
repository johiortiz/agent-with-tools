"""
Agente conversacional con herramientas.
Usa un LLM para razonar qué herramienta ejecutar y cuándo.
"""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from src.tools import Tools
from src.tool_executor import ToolExecutor
from src.logger import Logger

# Cargar variables de entorno
load_dotenv()

class Agent:
    """Agente conversacional que puede ejecutar herramientas."""
    
    def __init__(self, tools: Tools, executor: ToolExecutor, logger: Logger, model: str = "llama3.2"):
        self.tools = tools
        self.executor = executor
        self.logger = logger
        self.model = model
        
        # Configurar cliente de OpenAI (compatible con Ollama)
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
        # Historial de conversación
        self.conversation_history: List[Dict[str, str]] = []
    
    def _get_system_prompt(self) -> str:
        """Retorna el prompt del sistema con instrucciones para el agente."""
        tools_description = self.tools.get_tools_description()
        
        return f"""Eres un asistente de soporte de e-commerce con acceso a herramientas.

TU TAREA:
- Ayudar a los usuarios con sus pedidos, consultas y problemas.
- Usar las herramientas disponibles para obtener información real o ejecutar acciones.
- Ser claro y conciso en las respuestas.

HERRAMIENTAS DISPONIBLES:
{tools_description}

FORMATO PARA LLAMAR HERRAMIENTAS:
Cuando necesites usar una herramienta, responde EXACTAMENTE en este formato JSON:

{{"tool": "nombre_herramienta", "parameters": {{"param1": "valor1", "param2": "valor2"}}}}

Ejemplos:
- {{"tool": "get_order_status", "parameters": {{"order_id": "123"}}}}
- {{"tool": "create_support_ticket", "parameters": {{"reason": "Pedido no llegó", "customer_email": "juan@example.com"}}}}

REGLAS IMPORTANTES:
1. Si el usuario pregunta por un pedido, usa get_order_status o check_delivery_date.
2. Si el usuario reporta un problema, usa create_support_ticket.
3. Si necesitas enviar confirmación, usa send_confirmation_email.
4. ANTES de ejecutar create_support_ticket o send_confirmation_email, PIDE confirmación al usuario.
5. Si no estás seguro de qué herramienta usar, pregunta al usuario por más información.
6. Después de ejecutar una herramienta, explica el resultado al usuario en lenguaje natural.

CONVERSACIÓN:
Responde siempre en español.
"""
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parsea la respuesta del LLM para detectar si llama a una herramienta.
        
        Returns:
            {"type": "tool_call", "tool": "...", "parameters": {...}} o
            {"type": "message", "content": "..."}
        """
        # Buscar si hay una llamada a herramienta en formato JSON
        start = response_text.find('{"tool":')
        end = response_text.rfind("}") + 1
        
        if start != -1 and end != -1:
            # Extraer la llamada a herramienta
            tool_call_text = response_text[start:end]
            tool_name, parameters = self.executor.parse_tool_call(tool_call_text)
            
            if tool_name:
                return {
                    "type": "tool_call",
                    "tool": tool_name,
                    "parameters": parameters,
                    "original_response": response_text,
                }
        
        # Si no hay llamada a herramienta, es un mensaje normal
        return {
            "type": "message",
            "content": response_text.strip(),
        }
    
    def _execute_tool_call(self, tool_call: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """Ejecuta una llamada a herramienta."""
        tool_name = tool_call["tool"]
        parameters = tool_call["parameters"]
        
        # Verificar si requiere confirmación
        if self.executor.requires_confirmation(tool_name) and not user_confirmed:
            return {
                "type": "confirmation_required",
                "tool": tool_name,
                "parameters": parameters,
                "message": f"⚠️ Para ejecutar '{tool_name}', necesito tu confirmación. ¿Deseas continuar?",
            }
        
        # Ejecutar
        execution_result = self.executor.execute_tool(tool_name, parameters, confirmed=user_confirmed)
        
        # Extraer el resultado real de la herramienta
        tool_result = execution_result.get("result", execution_result)
        
        return {
            "type": "tool_result",
            "tool": tool_name,
            "result": tool_result,
        }
    
    def chat(self, user_message: str, user_confirmed: bool = False) -> str:
        """
        Procesa un mensaje del usuario y retorna una respuesta.
        
        Args:
            user_message: Mensaje del usuario.
            user_confirmed: Si el usuario confirmó una acción sensible.
        
        Returns:
            Respuesta del agente.
        """
        # Añadir mensaje al historial
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Obtener respuesta del LLM
        system_prompt = self._get_system_prompt()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
            ],
            temperature=0.7,
        )
        
        llm_response = response.choices[0].message.content
        
        # Parsear respuesta
        parsed = self._parse_llm_response(llm_response)
        
        if parsed["type"] == "tool_call":
            # El LLM quiere ejecutar una herramienta
            tool_result = self._execute_tool_call(parsed, user_confirmed)
            
            if tool_result["type"] == "confirmation_required":
                # Necesita confirmación
                self.conversation_history.append({"role": "assistant", "content": tool_result["message"]})
                return tool_result["message"]
            
            # Ejecutó la herramienta, ahora explicar el resultado
            result = tool_result["result"]
            tool_name = tool_result.get("tool", parsed["tool"])
            
            # Crear explicación en lenguaje natural
            explanation = self._explain_tool_result(tool_name, result)
            
            # Añadir al historial
            self.conversation_history.append({"role": "assistant", "content": explanation})
            
            return explanation
        
        else:
            # Respuesta normal
            self.conversation_history.append({"role": "assistant", "content": parsed["content"]})
            return parsed["content"]
    
    def _explain_tool_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """Explica el resultado de una herramienta en lenguaje natural."""
        if tool_name == "get_order_status":
            if "error" in result:
                return f"❌ {result['error']}"
            
            status_emoji = {
                "processing": "📦 En procesamiento",
                "in_transit": "🚚 En tránsito",
                "delivered": "✅ Entregado",
            }
            
            return (
                f"📋 **Estado del pedido {result.get('order_id', 'N/A')}:**\n"
                f"{status_emoji.get(result.get('status', 'unknown'), result.get('status', 'Desconocido'))}\n"
                f"📍 Ubicación actual: {result.get('location', 'N/A')}\n"
                f"📅 Entrega estimada: {result.get('estimated_delivery', 'N/A')}\n"
                f"📦 Items: {', '.join(result.get('items', []))}"
            )
        
        elif tool_name == "create_support_ticket":
            if "error" in result:
                return f"❌ {result['error']}"
            return f"✅ {result.get('message', 'Ticket creado exitosamente.')}"
        
        elif tool_name == "check_delivery_date":
            if "error" in result:
                return f"❌ {result['error']}"
            return f"📅 La entrega estimada para el pedido {result.get('order_id', 'N/A')} es el **{result.get('estimated_delivery', 'N/A')}**."
        
        elif tool_name == "send_confirmation_email":
            if "error" in result:
                return f"❌ {result['error']}"
            return f"✅ Email enviado a {result.get('email', 'N/A')}. Revisa tu bandeja de entrada."
        
        elif tool_name == "list_user_orders":
            if "error" in result:
                return f"❌ {result['error']}"
            
            orders_text = "\n".join([
                f"- Pedido {o['order_id']}: {o['status']} (entrega: {o['estimated_delivery']})"
                for o in result.get("orders", [])
            ])
            
            return (
                f"📋 **Pedidos de {result.get('user', 'Usuario')}:**\n"
                f"Total: {result.get('total_orders', 0)} pedidos\n\n"
                f"{orders_text}"
            )
        
        else:
            return f"✅ Herramienta ejecutada: {result}"
    
    def clear_history(self) -> None:
        """Limpia el historial de conversación."""
        self.conversation_history = []