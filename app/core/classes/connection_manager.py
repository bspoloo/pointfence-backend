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

        print(
            "ConnectionManager initialized. "
            "Active connections list created."
        )


    async def connect(self, websocket: WebSocket):

        await websocket.accept()

        if websocket not in self.active_connections:
            self.active_connections.append(websocket)

        print(
            "Unreal Engine conectado exitosamente."
        )


    async def disconnect(self, websocket: WebSocket):

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        print(
            "Unreal engine desconectado."
        )


    async def send_data(self, message: str):

        disconnected = []

        for connection in self.active_connections:

            try:

                await connection.send_text(message)

            except Exception as e:

                print(
                    f"[ERROR] Enviando mensaje: {e}"
                )

                disconnected.append(connection)

        for connection in disconnected:
            await self.disconnect(connection)


    async def send_mesh_binary(self, mesh):

        if not self.active_connections:
            print("No hay conexiones activas de UE4")
            return False

        try:

            vertices = np.asarray(
                mesh.vertices,
                dtype=np.float32
            )

            faces = np.asarray(
                mesh.faces,
                dtype=np.uint32
            )

            normals = np.asarray(
                mesh.vertex_normals,
                dtype=np.float32
            )

            if vertices.ndim != 2 or vertices.shape[1] != 3:
                print("Formato de vertices inválido")
                return False

            if faces.ndim != 2 or faces.shape[1] != 3:
                print("Formato de faces inválido")
                return False

            if normals.ndim != 2 or normals.shape[1] != 3:
                print("Formato de normales inválido")
                return False

            if len(vertices) != len(normals):
                print(
                    "La cantidad de normales no coincide "
                    "con los vertices"
                )
                return False

            num_vertices = len(vertices)
            num_faces = len(faces)

            print(f"Vertices: {num_vertices}")
            print(f"Triángulos: {num_faces}")

            header = struct.pack(
                "<II",
                num_vertices,
                num_faces
            )

            vertices = np.ascontiguousarray(
                vertices,
                dtype="<f4"
            )

            normals = np.ascontiguousarray(
                normals,
                dtype="<f4"
            )

            faces = np.ascontiguousarray(
                faces,
                dtype="<u4"
            )

            full_buffer = (
                header
                + vertices.tobytes()
                + normals.tobytes()
                + faces.tobytes()
            )

            print(
                f"Mesh binario: "
                f"{len(full_buffer) / (1024 * 1024):.2f} MB"
            )

            disconnected = []

            for connection in self.active_connections:

                try:

                    await connection.send_bytes(
                        full_buffer
                    )

                    print("Mesh enviado a Unreal.")

                except Exception as e:

                    print(
                        f"[ERROR] Enviando mesh: {e}"
                    )

                    disconnected.append(connection)

            for connection in disconnected:
                await self.disconnect(connection)

            return True

        except Exception as e:

            print(
                f"[ERROR] Preparando mesh binario: {e}"
            )

            return False