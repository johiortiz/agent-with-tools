"""
Agente conversacional con herramientas.
Usa un LLM para razonar qué herramienta ejecutar y cuándo.
"""

import os
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

from src.tools import Tools
from src.tool_executor import ToolExecutor
from src.logger import Logger

load_dotenv()


class Agent:
    """Agente conversacional que puede ejecutar herramientas."""

    def __init__(self, tools: Tools, executor: ToolExecutor, logger: Logger, model: str = "llama3.2"):
        self.tools = tools
        self.executor = executor
        self.logger = logger
        self.model = model

        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.conversation_history: List[Dict[str, str]] = []

        self.pending_tool = None
        self.pending_parameters = None

    def _get_system_prompt(self) -> str:
        tools_description = self.tools.get_tools_description()

        return f"""Eres un asistente de soporte de e-commerce.

        HERRAMIENTAS:
        {tools_description}

        REGLA DE ORO:
        - Si el usuario da un order_id, usa get_order_status o check_delivery_date.
        - Si el usuario da un email, usa list_user_orders.
        - Si el usuario reporta un problema, usa create_support_ticket.
        - Si necesitas una herramienta, responde SOLO un JSON, sin texto:
        {{"tool": "nombre", "parameters": {{"param": "valor"}}}}
        - Si NO necesitas herramienta, responde en español, sin JSON.
        - NO inventes IDs ni emails.
        """

    def _is_confirmation(self, text: str) -> bool:
        normalized = text.strip().lower()
        yes_words = ["sí", "si", "yes", "ok", "okay", "confirmo", "confirma", "adelante"]
        return any(word in normalized for word in yes_words)

    def _is_cancellation(self, text: str) -> bool:
        normalized = text.strip().lower()
        no_words = ["no", "cancelar", "cancela", "mejor no"]
        return any(word == normalized or word in normalized for word in no_words)

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        start = response_text.find('{"tool":')
        end = response_text.rfind("}") + 1

        if start != -1 and end != -1:
            tool_call_text = response_text[start:end]
            tool_name, parameters = self.executor.parse_tool_call(tool_call_text)

            if tool_name:
                return {
                    "type": "tool_call",
                    "tool": tool_name,
                    "parameters": parameters,
                    "original_response": response_text,
                }

        # No hay JSON válido: forzamos reintento
        return {
            "type": "message",
            "content": (
                "ERROR: Tu respuesta no es un JSON válido de herramienta. "
                "Responde SOLO con un JSON como: "
                '{"tool": "get_order_status", "parameters": {"order_id": "123"}}'
            ),
        }

    def _execute_tool_call(self, tool_call: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        tool_name = tool_call["tool"]
        parameters = tool_call["parameters"]

        if self.executor.requires_confirmation(tool_name) and not user_confirmed:
            self.pending_tool = tool_name
            self.pending_parameters = parameters
            return {
                "type": "confirmation_required",
                "tool": tool_name,
                "parameters": parameters,
                "message": (
                    f"⚠️ Para ejecutar '{tool_name}' necesito tu confirmación.\n"
                    f"Parámetros: {parameters}\n"
                    "Responde sí para continuar o no para cancelar."
                ),
            }

        execution_result = self.executor.execute_tool(
            tool_name, parameters, confirmed=user_confirmed
        )
        tool_result = execution_result.get("result", execution_result)

        self.pending_tool = None
        self.pending_parameters = None

        return {
            "type": "tool_result",
            "tool": tool_name,
            "result": tool_result,
        }

    def _explain_result(self, tool_name: str, result: Any) -> str:
        system_prompt = self._get_system_prompt()
        tool_context = (
            f"Se ejecutó la herramienta '{tool_name}'. "
            f"Resultado en JSON:\n{result}\n\n"
            "Explica este resultado al usuario en español, de forma clara y breve. "
            "NO llames a otra herramienta. NO uses JSON."
        )
        self.conversation_history.append({
            "role": "user",
            "content": tool_context,
        })

        explain_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
            ],
            temperature=0.3,
        )

        explanation = explain_response.choices[0].message.content.strip()
        self.conversation_history.append({
            "role": "assistant",
            "content": explanation,
        })
        return explanation

    def chat(self, user_message: str, user_confirmed: bool = False) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        if self.pending_tool is not None:
            if self._is_cancellation(user_message) and not self._is_confirmation(user_message):
                self.pending_tool = None
                self.pending_parameters = None
                msg = "De acuerdo, he cancelado la acción."
                self.conversation_history.append({"role": "assistant", "content": msg})
                return msg

            if self._is_confirmation(user_message) or user_confirmed:
                tool_result = self._execute_tool_call(
                    {
                        "tool": self.pending_tool,
                        "parameters": self.pending_parameters or {},
                    },
                    user_confirmed=True,
                )
                return self._explain_result(tool_result["tool"], tool_result["result"])

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
        parsed = self._parse_llm_response(llm_response)

        # Reintento si el modelo no dio JSON
        if parsed["type"] == "message" and "ERROR:" in parsed["content"]:
            self.conversation_history.append({"role": "assistant", "content": llm_response})
            self.conversation_history.append({"role": "user", "content": parsed["content"]})

            retry = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history,
                ],
                temperature=0.0,  # muy determinista
            )
            llm_response = retry.choices[0].message.content
            parsed = self._parse_llm_response(llm_response)

        if parsed["type"] == "tool_call":
            tool_result = self._execute_tool_call(parsed, user_confirmed)

            if tool_result["type"] == "confirmation_required":
                self.conversation_history.append({
                    "role": "assistant",
                    "content": tool_result["message"],
                })
                return tool_result["message"]

            return self._explain_result(tool_result["tool"], tool_result["result"])

        self.conversation_history.append({
            "role": "assistant",
            "content": parsed["content"],
        })
        return parsed["content"]

    def clear_history(self) -> None:
        self.conversation_history = []
        self.pending_tool = None
        self.pending_parameters = None