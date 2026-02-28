"""
services/llm_expander.py — Expansión de consultas usando GPT-2 (Text Continuation).
"""

import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class QueryExpanderModel:
    _instance: Optional["QueryExpanderModel"] = None
    _lock = asyncio.Lock()

    def __init__(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        logger.info("🔄 Cargando DeepESP/gpt2-spanish en CPU...")
        self.device = "cpu"
        model_name = "DeepESP/gpt2-spanish"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=torch.float32,
        )

        # Cuantización para optimizar RAM
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8
        )
        self.model.eval()

    @classmethod
    async def get_instance(cls) -> "QueryExpanderModel":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = await asyncio.to_thread(cls)
        return cls._instance

    def expand_query_sync(self, user_query: str) -> str:
        # Forzamos el autocompletado creando un patrón repetitivo
        prompt = f"Palabras relacionadas a {user_query}\n"

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        import torch

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=12,  # Generar más tokens para obtener frases más largas
                temperature=0.9,  # Aumentar la aleatoriedad para fomentar creatividad
                do_sample=True,  # Mantener el muestreo probabilístico
                top_k=50,  # Considerar solo las 50 palabras más probables
                top_p=0.9,  # Limitar a palabras dentro del 90% de probabilidad acumulada
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Recortar solo lo nuevo generado
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        # GPT-2 suele seguir escribiendo cosas como "Descripción: ..." si no lo paras.
        # Cortamos en el primer salto de línea para quedarnos solo con la lista de palabras.
        clean_response = response.split("\n")[0].strip()

        # Eliminamos signos de puntuación extraños al final si los hay
        clean_response = clean_response.rstrip(".,;")

        logger.info(f"🧠 GPT-2 Autocompletado: '{user_query}' -> '{clean_response}'")
        return clean_response


async def expand_query_async(user_query: str, max_keywords: int = 5) -> str:
    model = await QueryExpanderModel.get_instance()
    return await asyncio.to_thread(model.expand_query_sync, user_query)
