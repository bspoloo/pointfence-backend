from fastapi import WebSocket
import numpy as np
import struct

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
