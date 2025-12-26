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
        self.service = None
        
        # 2. Prioridad: Service Account (Credenciales completas)
        if os.path.exists(self.ruta_credenciales):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    self.ruta_credenciales, 
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
                self.service = build('drive', 'v3', credentials=creds)
                logger.info("Conectado a Google Drive mediante Service Account.")
            except Exception as e:
                logger.error(f"Error con Service Account: {e}")

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
        if not self.service: return None
        
        try:
            # 1. Obtener token fresco
            creds = self.service._http.credentials
            if creds.expired:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            token = creds.token

            # 2. Determinar si exportar o descargar
            meta = self.service.files().get(fileId=file_id, fields="mimeType").execute()
            mime_type = meta.get('mimeType', '')
            
            url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
            
            if mime_type.startswith('application/vnd.google-apps'):
                # Exportar Docs a PDF
                url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=application/pdf"
            
            # 3. Request con Streaming activado
            import requests
            headers = {"Authorization": f"Bearer {token}"}
            
            with requests.get(url, headers=headers, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=1024 * 1024): # 1MB chunks
                    yield chunk

        except Exception as e:
            logger.error(f"Error en streaming {file_id}: {e}")
            yield b""

servicio_drive = ServicioDrive()
