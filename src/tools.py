"""
Definición de herramientas que el agente puede ejecutar.
Cada herramienta tiene:
- Nombre
- Descripción (para que el LLM sepa cuándo usarla)
- Parámetros esperados
- Función que ejecuta la acción
"""

from typing import Dict, Any, Callable, List
from src.database import Database

class Tool:
    """Representa una herramienta que el agente puede ejecutar."""
    
    def __init__(self, name: str, description: str, parameters: List[str], func: Callable):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func
    
    def execute(self, **kwargs) -> Any:
        """Ejecuta la herramienta con los parámetros dados."""
        return self.func(**kwargs)

class Tools:
    """Colección de herramientas disponibles para el agente."""
    
    def __init__(self, db: Database):
        self.db = db
        self.tools = self._create_tools()
    
    def _create_tools(self) -> Dict[str, Tool]:
        """Crea todas las herramientas disponibles."""
        return {
            "get_order_status": Tool(
                name="get_order_status",
                description="Consulta el estado de un pedido por su ID. Retorna: status, location, estimated_delivery.",
                parameters=["order_id"],
                func=self.get_order_status,
            ),
            "create_support_ticket": Tool(
                name="create_support_ticket",
                description="Crea un ticket de soporte para un cliente. Requiere reason y customer_email.",
                parameters=["reason", "customer_email"],
                func=self.create_support_ticket,
            ),
            "check_delivery_date": Tool(
                name="check_delivery_date",
                description="Verifica la fecha de entrega estimada de un pedido.",
                parameters=["order_id"],
                func=self.check_delivery_date,
            ),
            "send_confirmation_email": Tool(
                name="send_confirmation_email",
                description="Envía un email de confirmación a un cliente. Requiere email y message.",
                parameters=["email", "message"],
                func=self.send_confirmation_email,
            ),
            "list_user_orders": Tool(
                name="list_user_orders",
                description="Lista todos los pedidos de un usuario por su email.",
                parameters=["email"],
                func=self.list_user_orders,
            ),
        }
    
    # === Implementación de las herramientas ===
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Consulta el estado de un pedido."""
        order = self.db.get_order(order_id)
        if not order:
            return {"error": f"Pedido {order_id} no encontrado"}
        
        return {
            "order_id": order["order_id"],
            "status": order["status"],
            "location": order["location"],
            "estimated_delivery": order["estimated_delivery"],
            "items": order["items"],
        }
    
    def create_support_ticket(self, reason: str, customer_email: str) -> Dict[str, Any]:
        """Crea un ticket de soporte."""
        ticket = self.db.create_ticket(reason, customer_email)
        return {
            "success": True,
            "ticket_id": ticket["ticket_id"],
            "message": f"Ticket creado exitosamente. ID: {ticket['ticket_id']}",
        }
    
    def check_delivery_date(self, order_id: str) -> Dict[str, Any]:
        """Verifica la fecha de entrega."""
        date = self.db.check_delivery_date(order_id)
        if not date:
            return {"error": f"Pedido {order_id} no encontrado"}
        
        return {
            "order_id": order_id,
            "estimated_delivery": date,
        }
    
    def send_confirmation_email(self, email: str, message: str) -> Dict[str, Any]:
        """Envía un email de confirmación (simulado)."""
        # En producción, esto usaría SendGrid, AWS SES, etc.
        return {
            "success": True,
            "email": email,
            "message": f"Email enviado a {email}: {message[:50]}...",
        }
    
    def list_user_orders(self, email: str) -> Dict[str, Any]:
        """Lista todos los pedidos de un usuario."""
        user = self.db.get_user(email)
        if not user:
            return {"error": f"Usuario {email} no encontrado"}
        
        orders = [o for o in self.db.get_all_orders() if o["customer_email"] == email]
        
        return {
            "user": user["name"],
            "email": email,
            "orders": orders,
            "total_orders": len(orders),
        }
    
    def get_tool_by_name(self, name: str) -> Tool:
        """Obtiene una herramienta por su nombre."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Tool]:
        """Obtiene todas las herramientas."""
        return list(self.tools.values())
    
    def get_tools_description(self) -> str:
        """Retorna una descripción de todas las herramientas (para el LLM)."""
        descriptions = []
        for tool in self.tools.values():
            desc = f"- {tool.name}: {tool.description}"
            desc += f" Parámetros: {', '.join(tool.parameters)}."
            descriptions.append(desc)
        return "\n".join(descriptions)
