import os
import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path

logger = logging.getLogger("ArcaDrive")

class ServicioDrive:
    def __init__(self):
        # 1. Configuración de Identidad
        self.folder_id = os.getenv("DRIVE_FOLDER_ID", "1LvZG-uIqhYCGMtV2xA54SHzuXOn30dng")
        self.api_key = os.getenv("DRIVE_API_KEY") 
        self.ruta_credenciales = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
        # Nuevo: Soporte para contenido JSON en variable de entorno (Render/Vercel friendly)
        self.contenido_credenciales = os.getenv("GOOGLE_CREDENTIALS_JSON") 
        
        self.service = None
        self.creds = None
        
        # 2. Prioridad: Service Account (JSON directo o Archivo)
        try:
            if self.contenido_credenciales:
                import json
                info = json.loads(self.contenido_credenciales)
                self.creds = service_account.Credentials.from_service_account_info(
                    info, scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
                logger.info("Conectado a Google Drive mediante JSON en Variable de Entorno.")
            elif os.path.exists(self.ruta_credenciales):
                self.creds = service_account.Credentials.from_service_account_file(
                    self.ruta_credenciales, 
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
                logger.info("Conectado a Google Drive mediante Archivo de Credenciales.")

            if self.creds:
                self.service = build('drive', 'v3', credentials=self.creds)

        except Exception as e:
            logger.error(f"Error autenticando Service Account: {e}")

        # 3. Fallback: API Key (Solo para carpetas públicas)
        if not self.service and self.api_key:
            try:
                self.service = build('drive', 'v3', developerKey=self.api_key)
                logger.info("Conectado a Google Drive mediante API Key (Acceso Público).")
            except Exception as e:
                logger.error(f"Error con API Key: {e}")

        if not self.service:
            logger.warning("Google Drive no está autenticado. La sincronización fallará.")

    def listar_archivos(self):
        """Lista todos los archivos compatibles en la carpeta de Drive configurada."""
        if not self.service or not self.folder_id:
            logger.error("Servicio Drive no configurado o falta FOLDER_ID.")
            return []

        query = f"'{self.folder_id}' in parents and trashed = false"
        archivos = []
        page_token = None
        
        try:
            while True:
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    pageSize=1000,
                    fields='nextPageToken, files(id, name, mimeType, size, md5Checksum)',
                    pageToken=page_token
                ).execute()
                
                archivos.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if not page_token:
                    break
            return archivos
        except Exception as e:
            logger.error(f"Error listando archivos de Drive: {e}")
            return []

    def generar_descarga(self, file_id):
        """Generador que hace streaming directo desde Drive sin usar RAM."""
        if not self.service: 
            yield b""
            return
        
        try:
            import requests
            
            # URLs Base
            url_descarga = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
            headers = {}
            params = {}

            # Estrategia de Autenticación para el Request manual
            if self.creds:
                # Caso A: Service Account (Token Bearer)
                if self.creds.expired:
                    from google.auth.transport.requests import Request
                    self.creds.refresh(Request())
                headers["Authorization"] = f"Bearer {self.creds.token}"
            elif self.api_key:
                # Caso B: API Key (Parametro key)
                params["key"] = self.api_key
            else:
                logger.error("No hay credenciales válidas para streaming.")
                yield b""
                return

            # Determinar MIME type real y nombre
            mime_type_real = "application/octet-stream"
            nombre_archivo = "archivo_descarga"
            
            try:
                meta = self.service.files().get(
                    fileId=file_id, 
                    fields="mimeType, name"
                ).execute()
                
                mime_type_real = meta.get('mimeType', 'application/octet-stream')
                nombre_archivo = meta.get('name', 'archivo')

                if mime_type_real.startswith('application/vnd.google-apps'):
                    # Si es Doc/Sheet/Slide nativo, forzar PDF
                    url_descarga = f"https://www.googleapis.com/drive/v3/files/{file_id}/export"
                    params["mimeType"] = "application/pdf"
                    mime_type_real = "application/pdf"
                    nombre_archivo += ".pdf"
            
            except Exception as e:
                logger.warning(f"No se pudieron obtener metadatos para {file_id}: {e}")

            # Streaming Request
            def iterador_stream():
                with requests.get(url_descarga, headers=headers, params=params, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=1024 * 1024): 
                        yield chunk
            
            return iterador_stream(), mime_type_real, nombre_archivo

        except Exception as e:
            logger.error(f"Error en streaming {file_id}: {e}")
            # Retornar generador vacío y mime fallback
            def empty_gen(): yield b""
            return empty_gen(), "application/octet-stream", "error.bin"

servicio_drive = ServicioDrive()
