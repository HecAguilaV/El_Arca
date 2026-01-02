import google.generativeai as genai
import os
import logging
from typing import Optional

logger = logging.getLogger("ArcaIA")

class ServicioIA:
    def __init__(self):
        self.api_key = os.getenv("VITE_GEMINI_API_KEY")
        self.model = None
        
        if not self.api_key:
            logger.warning("VITE_GEMINI_API_KEY no configurada en el backend.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Intentamos usar la versión 2.5 solicitada por el usuario
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash')
                    logger.info("Modelo configurado: gemini-2.5-flash")
                except Exception:
                    logger.warning("gemini-2.5-flash no disponible, usando fallback a 2.0-flash-exp")
                    self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception as e:
                logger.error(f"Error inicializando Gemini: {e}")
                self.model = None

    def definir_termino(self, termino: str, perspectiva: str = "universal") -> str:
        """Genera una definición teológica para un término dado."""
        if not self.api_key:
            return "Servicio de IA no configurado."

        # Prompt Universal: Académico, Neutral, Exegético y Teológico (sin sesgos denominacionales)
        base_prompt = """
        Eres un teólogo académico y erudito bíblico. Tu objetivo es definir términos teológicos de manera universal, neutral y rigurosa.
        
        Estructura de la respuesta:
        1. Etimología (Hebreo/Griego si aplica).
        2. Definición concisa.
        3. Uso bíblico principal (AT y NT).
        4. Desarrollo teológico (mencionando brevemente diferentes posturas históricas si hay controversia, pero manteniendo neutralidad).
        
        Evita jerga innecesaria. Sé claro, directo y pastoralmente útil pero academicamente sólido.
        No favorezcas la postura reformada, arminiana, católica u otra, a menos que el término sea específico de esa tradición.
        """

        prompt_final = f"{base_prompt}\n\nTérmino a definir: {termino}\n\nRespuesta en español formal:"

        try:
            respuesta = self.model.generate_content(prompt_final)
            return respuesta.text
        except Exception as e:
            logger.error(f"Error en Gemini IA: {e}")
            return f"Error técnico: {str(e)} (Verifica la API Key en Render)"

servicio_ia = ServicioIA()
