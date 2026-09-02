from fastapi import WebSocket
import numpy as np
import struct
import json
import os
import asyncio
import base64
class ConnectionManagerMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ConnectionManager(metaclass=ConnectionManagerMeta):
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("Unreal Engine conectado exitosamente.")
    
    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("Unreal engine desconectado")
    
    async def send_data(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[ERROR] {e}")
                self.disconnect(connection)

    async def send_point_cloud_binary(self, points_3d: np.ndarray, colors: np.ndarray):
        if not self.active_connections:
            print("No hay conexiones activas de UE4")
            return False
        
        num_points = len(points_3d)
        header = struct.pack('<I', num_points)

        data_buffer = bytearray()

        for i in range(num_points):
            data_buffer.extend(struct.pack('<fff', 
                                          points_3d[i, 0], 
                                          points_3d[i, 1], 
                                          points_3d[i, 2]))

            data_buffer.extend(struct.pack('<BBB', 
                                          colors[i, 0], 
                                          colors[i, 1], 
                                          colors[i, 2]))
        full_buffer = header + data_buffer

        for connection in self.active_connections:
            try:
                await connection.send_bytes(full_buffer)
            except Exception as e:
                print(f"[ERROR] {e}")

        return True

    async def send_glb_file(self, file_path: str, chunk_size: int = 65536):
            """Envía un archivo GLB en chunks a través de WebSocket"""
            if not self.active_connections:
                print("No hay conexiones activas")
                return False
            
            try:
                if not os.path.exists(file_path):
                    print(f"Archivo no encontrado: {file_path}")
                    return False
                
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                print(f"Enviando archivo: {file_name} ({file_size} bytes)")
                
                metadata = {
                    "type": "glb_start",
                    "filename": file_name,
                    "file_size": file_size,
                    "chunk_size": chunk_size
                }
                
                for connection in self.active_connections:
                    try:
                        await connection.send_text(json.dumps(metadata))
                    except Exception as e:
                        print(f"[ERROR] Enviando metadatos: {e}")
                
                total_sent = 0
                chunk_index = 0
                
                with open(file_path, "rb") as file:
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            break
                        
                        encoded_chunk = base64.b64encode(chunk).decode('utf-8')
                        
                        chunk_data = {
                            "type": "glb_chunk",
                            "data": encoded_chunk,
                            "chunk_index": chunk_index,
                            "total_sent": total_sent,
                            "total_size": file_size
                        }
                        
                        for connection in self.active_connections:
                            try:
                                await connection.send_text(json.dumps(chunk_data))
                            except Exception as e:
                                print(f"[ERROR] Enviando chunk: {e}")
                        
                        total_sent += len(chunk)
                        chunk_index += 1
                        
                        await asyncio.sleep(0.001)
                        
                        progress = (total_sent / file_size) * 100
                        if chunk_index % 10 == 0:
                            print(f"Progreso: {progress:.1f}%")
                
                completion = {
                    "type": "glb_end",
                    "filename": file_name,
                    "total_bytes": file_size,
                    "total_chunks": chunk_index
                }
                
                for connection in self.active_connections:
                    try:
                        await connection.send_text(json.dumps(completion))
                    except Exception as e:
                        print(f"[ERROR] Enviando completado: {e}")
                
                print(f"Archivo {file_name} enviado exitosamente en {chunk_index} chunks")
                return True
                
            except Exception as e:
                print(f"[ERROR] Enviando archivo GLB: {e}")
                error_msg = {
                    "type": "error",
                    "message": f"Error enviando archivo: {str(e)}"
                }
                for connection in self.active_connections:
                    try:
                        await connection.send_text(json.dumps(error_msg))
                    except:
                        pass
                return False