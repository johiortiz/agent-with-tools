"""
Ejecutor de herramientas: valida y ejecuta las herramientas solicitadas por el agente.
También maneja confirmaciones para acciones sensibles.
"""

import json
from typing import Dict, Any, Optional, Tuple
from src.tools import Tools, Tool
from src.logger import Logger

class ToolExecutor:
    """Ejecuta y valida herramientas solicitadas por el agente."""
    
    def __init__(self, tools: Tools, logger: Logger):
        self.tools = tools
        self.logger = logger
        
        # Herramientas que requieren confirmación
        self.sensitive_tools = {
            "create_support_ticket",
            "send_confirmation_email",
        }
    
    def parse_tool_call(self, tool_call_text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parsea el texto de llamada a herramienta del LLM.
        
        Espera formato: {"tool": "nombre_herramienta", "parameters": {"param1": "valor1"}}
        
        Returns:
            (tool_name, parameters) o (None, None) si hay error.
        """
        try:
            # Extraer JSON del texto
            start = tool_call_text.find("{")
            end = tool_call_text.rfind("}") + 1
            
            if start == -1 or end == -1:
                return None, None
            
            tool_call = json.loads(tool_call_text[start:end])
            
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            
            return tool_name, parameters
        
        except (json.JSONDecodeError, KeyError):
            return None, None
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida que la llamada a herramienta sea correcta.
        
        Returns:
            (es_valido, mensaje_de_error)
        """
        tool = self.tools.get_tool_by_name(tool_name)
        
        if not tool:
            return False, f"Herramienta '{tool_name}' no existe"
        
        # Verificar parámetros requeridos
        missing_params = [p for p in tool.parameters if p not in parameters]
        if missing_params:
            return False, f"Parámetros faltantes: {', '.join(missing_params)}"
        
        return True, ""
    
    def requires_confirmation(self, tool_name: str) -> bool:
        """Verifica si la herramienta requiere confirmación del usuario."""
        return tool_name in self.sensitive_tools
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], confirmed: bool = True) -> Dict[str, Any]:
        """
        Ejecuta una herramienta.
        
        Args:
            tool_name: Nombre de la herramienta.
            parameters: Parámetros para la herramienta.
            confirmed: Si el usuario confirmó (para herramientas sensibles).
        
        Returns:
            Resultado de la ejecución.
        """
        # Validar
        is_valid, error_msg = self.validate_tool_call(tool_name, parameters)
        if not is_valid:
            return {"error": error_msg}
        
        # Verificar confirmación
        if self.requires_confirmation(tool_name) and not confirmed:
            return {
                "requires_confirmation": True,
                "tool": tool_name,
                "parameters": parameters,
                "message": f"La acción '{tool_name}' requiere confirmación. ¿Deseas continuar?",
            }
        
        # Ejecutar
        tool = self.tools.get_tool_by_name(tool_name)
        result = tool.execute(**parameters)
        
        # Loguear
        self.logger.log_execution(tool_name, parameters, result)
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result,
        }
