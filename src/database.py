"""
Base de datos simulada para el agente.
En producción, esto sería una DB real (PostgreSQL, MongoDB, etc.).
"""

from typing import Dict, Any, List, Optional

class Database:
    """Base de datos simulada con pedidos, tickets y usuarios."""
    
    def __init__(self):
        # Pedidos simulados
        self.orders = {
            "123": {
                "order_id": "123",
                "customer_email": "juan@example.com",
                "status": "in_transit",
                "location": "Madrid",
                "estimated_delivery": "2026-09-20",
                "items": ["Laptop", "Mouse"],
            },
            "456": {
                "order_id": "456",
                "customer_email": "maria@example.com",
                "status": "delivered",
                "location": "Barcelona",
                "estimated_delivery": "2026-09-18",
                "items": ["Teclado", "Monitor"],
            },
            "789": {
                "order_id": "789",
                "customer_email": "pedro@example.com",
                "status": "processing",
                "location": "Valencia",
                "estimated_delivery": "2026-09-22",
                "items": ["Auriculares"],
            },
        }
        
        # Tickets de soporte simulados
        self.tickets = []
        
        # Usuarios simulados
        self.users = {
            "juan@example.com": {"name": "Juan", "active": True},
            "maria@example.com": {"name": "María", "active": True},
            "pedro@example.com": {"name": "Pedro", "active": True},
        }
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido por ID."""
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Obtiene todos los pedidos."""
        return list(self.orders.values())
    
    def create_ticket(self, reason: str, customer_email: str) -> Dict[str, Any]:
        """Crea un ticket de soporte."""
        ticket_id = f"T{len(self.tickets) + 1:03d}"
        ticket = {
            "ticket_id": ticket_id,
            "reason": reason,
            "customer_email": customer_email,
            "status": "open",
            "created_at": "2026-09-19",
        }
        self.tickets.append(ticket)
        return ticket
    
    def get_tickets_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Obtiene tickets por email de cliente."""
        return [t for t in self.tickets if t["customer_email"] == email]
    
    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por email."""
        return self.users.get(email)
    
    def check_delivery_date(self, order_id: str) -> Optional[str]:
        """Verifica la fecha de entrega estimada."""
        order = self.get_order(order_id)
        if order:
            return order["estimated_delivery"]
        return None
