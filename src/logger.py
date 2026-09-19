"""
Registro de ejecuciones de herramientas.
Guarda cada herramienta ejecutada con timestamp, parámetros y resultado.
"""

import json
from datetime import datetime
from typing import Dict, Any, List

class Logger:
    """Registra todas las ejecuciones de herramientas."""
    
    def __init__(self, log_path: str = "data/execution_log.json"):
        self.log_path = log_path
        self.logs = self._load_logs()
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """Carga los logs existentes desde el archivo."""
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_logs(self) -> None:
        """Guarda los logs en el archivo."""
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
    
    def log_execution(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Registra una ejecución de herramienta.
        
        Args:
            tool_name: Nombre de la herramienta ejecutada.
            parameters: Parámetros usados.
            result: Resultado de la ejecución.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "parameters": parameters,
            "result": result,
        }
        
        self.logs.append(log_entry)
        self._save_logs()
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Obtiene todos los logs."""
        return self.logs
    
    def get_logs_by_tool(self, tool_name: str) -> List[Dict[str, Any]]:
        """Obtiene logs de una herramienta específica."""
        return [log for log in self.logs if log["tool"] == tool_name]
    
    def clear_logs(self) -> None:
        """Limpia todos los logs."""
        self.logs = []
        self._save_logs()
