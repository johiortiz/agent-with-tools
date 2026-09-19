#!/usr/bin/env python3
"""
Punto de entrada para el Agente con Herramientas.

Uso:
    python main.py                    # Modo interactivo
    python main.py --demo             # Modo demostración
"""

import argparse
from src.database import Database
from src.tools import Tools
from src.logger import Logger
from src.tool_executor import ToolExecutor
from src.agent import Agent

def create_agent() -> Agent:
    """Crea y retorna una instancia del agente."""
    db = Database()
    tools = Tools(db)
    logger = Logger()
    executor = ToolExecutor(tools, logger)
    agent = Agent(tools, executor, logger, model="llama3.2")
    return agent

def interactive_mode():
    """Ejecuta el agente en modo interactivo (chat)."""
    print("=" * 60)
    print(" " * 15 + "🤖 AGENTE CON HERRAMIENTAS 🤖")
    print("=" * 60)
    print("\nEscribe 'salir' para terminar, 'limpiar' para reiniciar conversación.")
    print("Ejemplos de consultas:")
    print("  - '¿Dónde está mi pedido 123?'")
    print("  - 'Quiero reportar un problema con mi pedido'")
    print("  - '¿Cuándo llega mi pedido 456?'")
    print("  - 'Lista mis pedidos con email juan@example.com'")
    print()
    
    agent = create_agent()
    
    while True:
        try:
            user_input = input("👤 Tú: ").strip()
            
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\n👋 ¡Hasta luego!")
                break
            
            if user_input.lower() == "limpiar":
                agent.clear_history()
                print("🧹 Conversación reiniciada.\n")
                continue
            
            if not user_input:
                continue
            
            response = agent.chat(user_input)
            print(f"\n🤖 Agente: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

def demo_mode():
    """Ejecuta una demostración automática del agente."""
    print("=" * 60)
    print(" " * 18 + "🎬 MODO DEMOSTRACIÓN 🎬")
    print("=" * 60)
    
    agent = create_agent()
    
    # Escenario 1: Consultar pedido
    print("\n--- Escenario 1: Consultar estado de pedido ---")
    user_msg = "¿Dónde está mi pedido 123?"
    print(f"👤 Tú: {user_msg}")
    response = agent.chat(user_msg)
    print(f"🤖 Agente: {response}\n")
    
    # Escenario 2: Verificar fecha de entrega
    print("--- Escenario 2: Verificar fecha de entrega ---")
    user_msg = "¿Cuándo llega el pedido 456?"
    print(f"👤 Tú: {user_msg}")
    response = agent.chat(user_msg)
    print(f"🤖 Agente: {response}\n")
    
    # Escenario 3: Listar pedidos de usuario
    print("--- Escenario 3: Listar pedidos de usuario ---")
    user_msg = "Lista mis pedidos con email maria@example.com"
    print(f"👤 Tú: {user_msg}")
    response = agent.chat(user_msg)
    print(f"🤖 Agente: {response}\n")
    
    # Escenario 4: Crear ticket (requiere confirmación)
    print("--- Escenario 4: Crear ticket de soporte ---")
    user_msg = "Quiero reportar un problema, mi pedido no llegó"
    print(f"👤 Tú: {user_msg}")
    response = agent.chat(user_msg)
    print(f"🤖 Agente: {response}\n")
    
    # Confirmar creación de ticket
    user_msg = "Sí, confirma el ticket con email juan@example.com"
    print(f"👤 Tú: {user_msg}")
    response = agent.chat(user_msg, user_confirmed=True)
    print(f"🤖 Agente: {response}\n")
    
    print("=" * 60)
    print("✅ Demostración completada!")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Agente con Herramientas")
    parser.add_argument("--demo", action="store_true", help="Ejecutar en modo demostración")
    args = parser.parse_args()
    
    if args.demo:
        demo_mode()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
