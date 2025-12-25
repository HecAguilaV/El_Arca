import chromadb
from chromadb.config import Settings
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("ArcaVector")

class ServicioVectorial:
    def __init__(self):
        # Configuración de Chroma Cloud (Proporcionada por el usuario)
        self.api_key = os.getenv("CHROMA_API_KEY", "ck-GK4oZxwwX6JaxyKbeXrBFfGABLCrRQzisKK4i96Z9gXs")
        self.tenant = "34c6a845-7f29-408c-a89d-03d8cb287980"
        self.database = "arca_db"
        
        try:
            # Usamos el cliente oficial de Chroma Cloud
            self.client = chromadb.CloudClient(
                api_key=self.api_key,
                tenant=self.tenant,
                database=self.database
            )
            self.collection = self.client.get_or_create_collection(
                name="biblioteca_teologica",
                metadata={"description": "Embeddings de libros teológicos para RAG"}
            )
            logger.info("Conectado a ChromaDB exitosamente.")
        except Exception as e:
            logger.error(f"Error conectando a ChromaDB: {e}")
            self.client = None

    def indexar_fragmento(self, id_libro: str, texto: str, metadatos: Dict[str, Any]):
        """Indexa un fragmento de texto en la base vectorial."""
        if not self.client: return
        
        self.collection.add(
            documents=[texto],
            metadatas=[metadatos],
            ids=[f"{id_libro}_{hash(texto)}"]
        )

    def buscar_similitud(self, consulta: str, n_resultados: int = 5):
        """Busca los fragmentos más relevantes para una consulta."""
        if not self.client: return []
        
        resultados = self.collection.query(
            query_texts=[consulta],
            n_results=n_resultados
        )
        return resultados
