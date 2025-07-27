#!/usr/bin/env python3
"""
AI interface for Sarek AI Assistant
"""

import requests
from typing import List, Tuple
from .config import ConfigManager
from .database import EnhancedMemoryDB
from ..constants import OLLAMA_URL, DEFAULT_MODEL, MODEL_ROUTING


class AIInterface:
    """Interface for communicating with AI models via Ollama"""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.db = EnhancedMemoryDB()

    def auto_select_model(self, user_input: str, context: str = "") -> str:
        """Intelligently select the best model for the task"""
        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in [
            'code', 'function', 'class', 'debug', 'algorithm', 'programming',
            'syntax', 'bug', 'error', 'compile', 'refactor'
        ]):
            return MODEL_ROUTING.get('code_analysis', 'codellama')

        elif any(word in user_input_lower for word in [
            'calculate', 'math', 'equation', 'formula', 'solve'
        ]):
            return MODEL_ROUTING.get('math_problems', 'mistral')

        elif any(word in user_input_lower for word in [
            'write', 'story', 'creative', 'poem', 'narrative'
        ]):
            return MODEL_ROUTING.get('creative_writing', 'llama2')

        return MODEL_ROUTING.get('general_chat', 'mistral')

    def build_context_prompt(self, session_name: str, user_input: str,
                             model: str = None) -> Tuple[str, str]:
        """Build context-aware prompt with conversation history"""
        if not model:
            model = self.auto_select_model(user_input)

        recent_conversations = self.db.get_recent_context(
            session_name, limit=self.config.get('context_limit', 3)
        )

        system_prompts = {
            'mistral': "You are Sarek, a logical and helpful AI assistant named after Spock's father. Provide clear, technical explanations with Vulcan-like precision.",
            'codellama': "You are Sarek, a code analysis expert. Provide detailed technical explanations of code, algorithms, and programming concepts.",
            'llama2': "You are Sarek, a creative and analytical assistant. Help with both technical and creative tasks with logical precision."
        }

        system_prompt = system_prompts.get(model, system_prompts['mistral'])

        if not recent_conversations:
            return f"{system_prompt}\n\nUser: {user_input}\nAssistant:", ""

        context_parts = [system_prompt, "\nPrevious conversation context:"]
        for conv in recent_conversations:
            context_parts.append(f"User: {conv.user_input}")
            context_parts.append(f"Assistant: {conv.ai_response}")

        context = "\n".join(context_parts)
        full_prompt = f"{context}\n\nCurrent question:\nUser: {user_input}\nAssistant:"

        return full_prompt, context

    def ask_model(self, prompt: str, model: str = None) -> str:
        """Query specified model via Ollama"""
        if not model:
            model = self.config.get('default_model', DEFAULT_MODEL)

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["response"]

        except requests.exceptions.Timeout:
            return f"❌ Request timed out. Model '{model}' might be processing a large request."
        except requests.exceptions.ConnectionError:
            return f"❌ Cannot connect to Ollama. Make sure it's running with `ollama serve`"
        except requests.exceptions.HTTPError as e:
            if "404" in str(e):
                return f"❌ Model '{model}' not found. Available models: {self.get_available_models()}"
            return f"❌ HTTP error: {e}"
        except Exception as e:
            return f"❌ Error querying model '{model}': {e}"

    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'].split(':')[0] for model in models]
        except Exception:
            pass
        return ['mistral', 'codellama', 'llama2']  # Default fallback

    def query_with_context(self, session_name: str, user_input: str,
                           model: str = None) -> Tuple[str, str]:
        """Query AI with context and return response + context used"""
        full_prompt, context = self.build_context_prompt(session_name, user_input, model)
        response = self.ask_model(full_prompt, model)
        return response, context