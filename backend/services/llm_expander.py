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

        logger.info("🔄 Cargando HuggingFaceTB/SmolLM2-135M en CPU...")
        self.device = "cpu"
        model_name = "HuggingFaceTB/SmolLM2-135M"

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
        import re
        # Few-shot prompt que guía al modelo a generar una lista separada por comas
        prompt = (
            f"{user_query}"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        import torch

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=32,            # Ligeramente aumentado para permitir más etiquetas
                temperature=0.75,             # Aumentado (antes 0.5) para mayor creatividad y diversidad
                do_sample=True,
                top_k=50,
                top_p=0.95,                   # Aumentado (antes 0.9) para considerar una cola más larga de vocabulario
                repetition_penalty=1.2,       # Penaliza la repetición para evitar que genere la misma etiqueta varias veces
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Recortar solo lo nuevo generado (todo lo que viene después del prompt)
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        # Quedarnos solo con la primera línea (el modelo puede generar el siguiente ejemplo)
        first_line = response.split("\n")[0]

        # Extraer tokens individuales (palabras alfanuméricas) y reconstruir como lista CSV
        tokens = re.findall(r"[\w'\-]+", first_line)

        if tokens:
            clean_response = ", ".join(tokens)
        else:
            # Fallback: usar las palabras de la query original
            clean_response = ", ".join(user_query.split())

        logger.info(f"🧠 SmolLM keywords: '{user_query}' -> '{clean_response}'")
        return clean_response


async def expand_query_async(user_query: str, max_keywords: int = 5) -> str:
    model = await QueryExpanderModel.get_instance()
    return await asyncio.to_thread(model.expand_query_sync, user_query)
