# 🤖 Agente con Herramientas

Agente conversacional de e-commerce capaz de ejecutar acciones reales mediante herramientas: consultar pedidos, crear tickets de soporte, verificar fechas de entrega y enviar emails.

<p align="center">
  <a href="#-descripción">Descripción</a> •
  <a href="#-instalación">Instalación</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-arquitectura">Arquitectura</a> •
  <a href="#-conceptos-aprendidos">Conceptos</a> •
  <a href="#-dificultades">Dificultades</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 🎯 Descripción

<p style="background-color: #f6f8fa; padding: 15px; border-left: 4px solid #58a6ff; border-radius: 4px;">
  Este proyecto demuestra la diferencia entre un <strong>chatbot</strong> (solo genera texto) y un <strong>agente</strong> (razona, llama herramientas y modifica información de forma controlada).
</p>

### Características principales

| Característica | Descripción |
|----------------|-------------|
| 🧠 **Razonamiento** | El LLM decide qué herramienta usar según el contexto |
| 🛠️ **Herramientas** | 5 herramientas: consultar pedido, crear ticket, verificar entrega, enviar email, listar pedidos |
| ✅ **Validación** | Parámetros validados antes de ejecutar |
| ⚠️ **Confirmación** | Acciones sensibles requieren confirmación del usuario |
| 📝 **Logging** | Registro de cada herramienta ejecutada |
| 🏠 **100% local** | Usa Ollama, sin APIs externas |

### Herramientas disponibles

```python
get_order_status(order_id)           # Consulta estado de un pedido
create_support_ticket(reason, email) # Crea ticket de soporte
check_delivery_date(order_id)        # Verifica fecha de entrega
send_confirmation_email(email, msg)  # Envía email de confirmación
list_user_orders(email)              # Lista pedidos de un usuario
```

---

## 🚀 Instalación

### Requisitos previos

<div style="background-color: #fff8c5; padding: 15px; border-left: 4px solid #d9d0a5; border-radius: 4px;">
  <strong>⚠️ Antes de empezar:</strong>
  <ul>
    <li>Python 3.10+</li>
    <li>Ollama instalado (<a href="https://ollama.ai">ollama.ai</a>)</li>
    <li>Modelo <code>llama3.2</code> descargado</li>
  </ul>
</div>

### Pasos

<ol>
  <li>
    <strong>Clonar el repositorio:</strong>
    <pre><code>git clone https://github.com/tu-usuario/agent-with-tools.git
cd agent-with-tools</code></pre>
  </li>
  <li>
    <strong>Crear entorno virtual:</strong>
    <pre><code>python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate</code></pre>
  </li>
  <li>
    <strong>Instalar dependencias:</strong>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>
    <strong>Verificar Ollama:</strong>
    <pre><code>ollama pull llama3.2</code></pre>
  </li>
</ol>

---

## 📖 Uso

### Modo demostración

<pre><code>python main.py --demo</code></pre>

Ejecuta 5 escenarios automáticos:

1. Consultar estado de pedido `#123`
2. Verificar fecha de entrega `#456`
3. Listar pedidos de usuario
4. Crear ticket de soporte (con confirmación)
5. Enviar email de confirmación

### Modo interactivo (chat)

<pre><code>python main.py</code></pre>

Ejemplos de consultas:

```
👤 Tú: ¿Dónde está mi pedido 123?
🤖 Agente: 📋 Estado del pedido 123: 🚚 En tránsito...

👤 Tú: Quiero reportar un problema con mi pedido
🤖 Agente: ⚠️ Para ejecutar 'create_support_ticket', necesito tu confirmación...

👤 Tú: Sí, confirma con email juan@example.com
🤖 Agente: ✅ Ticket creado exitosamente. ID: T001
```

### Comandos del chat

| Comando | Función |
|---------|---------|
| `salir` | Termina la conversación |
| `limpiar` | Reinicia el historial |

---

## 🏗️ Arquitectura

<pre><code>agent-with-tools/
│
├── src/
│   ├── agent.py              # Agente (LLM + razonamiento)
│   ├── tools.py              # Definición de herramientas
│   ├── tool_executor.py      # Ejecuta y valida herramientas
│   ├── database.py           # Base de datos simulada
│   └── logger.py             # Registro de ejecuciones
│
├── data/
│   └── execution_log.json    # Log de herramientas ejecutadas
│
├── main.py                   # Punto de entrada
└── README.md                 # Este archivo</code></pre>

### Flujo de ejecución

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Usuario    │ ──► │     LLM      │ ──► │   Tool       │
│  (input)     │     │ (razonamiento)│     │  Executor    │
└──────────────┘     └──────────────┘     └──────────────┘
                            ▲                    │
                            │                    ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   Respuesta  │ ◄── │  Herramientas │
                     │   (output)   │     │   (acción)    │
                     └──────────────┘     └──────────────┘
```

---

## 📚 Conceptos aprendidos

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
  <div style="background-color: #f6f8fa; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de;">
    <h4 style="margin-top: 0; color: #0969da;">🤖 Agentes de IA</h4>
    <ul>
      <li>Diferencia chatbot vs agente</li>
      <li>Tool calling con LLMs</li>
      <li>Prompt engineering para agentes</li>
    </ul>
  </div>
  <div style="background-color: #f6f8fa; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de;">
    <h4 style="margin-top: 0; color: #0969da;">🏛️ Arquitectura</h4>
    <ul>
      <li>Separación de responsabilidades</li>
      <li>Patrón Command (herramientas)</li>
      <li>Validación de parámetros</li>
    </ul>
  </div>
  <div style="background-color: #f6f8fa; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de;">
    <h4 style="margin-top: 0; color: #0969da;">🔒 Seguridad</h4>
    <ul>
      <li>Confirmación para acciones sensibles</li>
      <li>Logging de ejecuciones</li>
      <li>Validación de inputs</li>
    </ul>
  </div>
  <div style="background-color: #f6f8fa; padding: 15px; border-radius: 6px; border: 1px solid #d0d7de;">
    <h4 style="margin-top: 0; color: #0969da;">🐍 Python</h4>
    <ul>
      <li>Clases y métodos</li>
      <li>JSON parsing</li>
      <li>Manejo de excepciones</li>
      <li>Type hints</li>
    </ul>
  </div>
</div>

---

## ⚠️ Dificultades encontradas

<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background-color: #f6f8fa;">
      <th style="padding: 12px; border: 1px solid #d0d7de; text-align: left;">Problema</th>
      <th style="padding: 12px; border: 1px solid #d0d7de; text-align: left;">Solución</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        <strong>LLM no sigue formato JSON</strong><br>
        <small>A veces el LLM responde texto libre en vez de JSON</small>
      </td>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        Prompt más explícito con ejemplos claros del formato esperado
      </td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        <strong>Parámetros incorrectos</strong><br>
        <small>El LLM inventa parámetros que no existen</small>
      </td>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        Validación estricta en ToolExecutor antes de ejecutar
      </td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        <strong>Confirmación de acciones sensibles</strong><br>
        <small>Cómo evitar que el agente ejecute sin permiso</small>
      </td>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        Lista de herramientas sensibles + flag user_confirmed
      </td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        <strong>Explicar resultados al usuario</strong><br>
        <small>Los resultados crudos son muy técnicos</small>
      </td>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        Función _explain_tool_result que traduce a lenguaje natural
      </td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        <strong>Historial de conversación</strong><br>
        <small>El LLM olvida el contexto</small>
      </td>
      <td style="padding: 12px; border: 1px solid #d0d7de;">
        conversation_history que se pasa en cada llamada al LLM
      </td>
    </tr>
  </tbody>
</table>

---

## 🔜 Roadmap

<details open>
  <summary style="font-weight: bold; font-size: 1.2em; cursor: pointer; padding: 10px; background-color: #f6f8fa; border-radius: 6px;">
    📋 v1.1 - Mejoras de herramientas
  </summary>
  <div style="padding: 15px;">
    <ul>
      <li>Herramientas asíncronas: soporte para async/await</li>
      <li>Herramientas en paralelo: ejecutar varias a la vez</li>
      <li>Reintentos automáticos: retry con backoff</li>
    </ul>
  </div>
</details>

<details>
  <summary style="font-weight: bold; font-size: 1.2em; cursor: pointer; padding: 10px; background-color: #f6f8fa; border-radius: 6px;">
    🌐 v1.2 - Integraciones reales
  </summary>
  <div style="padding: 15px;">
    <ul>
      <li>API de envíos real</li>
      <li>Email real (SendGrid o AWS SES)</li>
      <li>Base de datos real (PostgreSQL o MongoDB)</li>
    </ul>
  </div>
</details>

<details>
  <summary style="font-weight: bold; font-size: 1.2em; cursor: pointer; padding: 10px; background-color: #f6f8fa; border-radius: 6px;">
    🧠 v1.3 - Mejoras del agente
  </summary>
  <div style="padding: 15px;">
    <ul>
      <li>Memoria a largo plazo</li>
      <li>Multi-paso: consultar, crear ticket y enviar email</li>
      <li>Auto-corrección si una herramienta falla</li>
    </ul>
  </div>
</details>

<details>
  <summary style="font-weight: bold; font-size: 1.2em; cursor: pointer; padding: 10px; background-color: #f6f8fa; border-radius: 6px;">
    🎨 v1.4 - Interfaz web
  </summary>
  <div style="padding: 15px;">
    <ul>
      <li>Frontend en React/Astro</li>
      <li>Dashboard de logs</li>
      <li>Exportar logs a CSV/JSON</li>
    </ul>
  </div>
</details>

<details>
  <summary style="font-weight: bold; font-size: 1.2em; cursor: pointer; padding: 10px; background-color: #f6f8fa; border-radius: 6px;">
    🔒 v1.5 - Seguridad y permisos
  </summary>
  <div style="padding: 15px;">
    <ul>
      <li>Autenticación de usuarios</li>
      <li>Permisos por rol</li>
      <li>Rate limiting</li>
    </ul>
  </div>
</details>

---

## 📄 Licencia

<p style="background-color: #f6f8fa; padding: 15px; border-radius: 4px;">
  <strong>MIT License</strong>
</p>

---

## 🤝 Contribuciones

<div style="background-color: #ddf4ff; padding: 15px; border-left: 4px solid #0969da; border-radius: 4px;">
  <strong>Las contribuciones son bienvenidas.</strong><br>
  Abre un issue o PR para:
  <ul>
    <li>Reportar bugs</li>
    <li>Sugerir nuevas herramientas</li>
    <li>Mejorar el razonamiento del agente</li>
  </ul>
</div>

---

## 📧 Contacto

<p align="center">
  <strong>Johi Ortiz Vallejos</strong>
</p>

<p align="center" style="color: #8b949e; font-size: 0.9em;">
  Proyecto creado como material educativo para aprender agentes de IA con herramientas.
</p>

<p align="center">
  <strong>Hecho con ❤️ para aprender agentes autónomos</strong>
</p>