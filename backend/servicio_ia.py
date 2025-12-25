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

    def definir_termino(self, termino: str, perspectiva: str = "reformado") -> str:
        """Genera una definición teológica para un término dado."""
        if not self.api_key:
            return "Servicio de IA no configurado."

        prompts = {
            "reformado": "Eres un teólogo reformado de la tradición de Calvino y los Sínodos de Dort. Define el siguiente término con rigor doctrinal y citas bíblicas:",
            "puritano": "Eres un pastor puritano del siglo XVII. Define el siguiente término con un enfoque práctico y experimental, enfocado en la piedad:",
            "academico": "Eres un erudito bíblico especializado en exégesis y lenguas originales. Define el siguiente término desde una perspectiva lingüística e histórica:",
            "pastoral": "Eres un consejero pastoral enfocado en la aplicación del evangelio. Define el siguiente término de forma clara y reconfortante:"
        }

        enfoque = prompts.get(perspectiva, prompts["reformado"])
        prompt_final = f"{enfoque}\n\nTérmino: {termino}\n\nRespuesta en español, con un tono formal y profesional."

        try:
            respuesta = self.model.generate_content(prompt_final)
            return respuesta.text
        except Exception as e:
            logger.error(f"Error en Gemini IA: {e}")
            return f"Error técnico: {str(e)} (Verifica la API Key en Render)"

servicio_ia = ServicioIA()
