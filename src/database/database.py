from datetime import datetime

import psycopg2


class Database:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self._connect()

    def _connect(self):
        """Establece una conexión a la base de datos."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Conexión exitosa a la base de datos.")
        except psycopg2.Error as e:
            print("Error al conectar a la base de datos:", e)

    def insertar_documento(self, nombre_archivo, ruta_archivo, fecha):
        """Inserta un documento en la tabla documentos."""
        if not self.conn:
            print("Conexión no disponible.")
            return
        try:
            # Convert the date format if it's in DD/MM/YYYY format
            fecha = datetime.strptime(fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO documentos (nombre, ruta_archivo, fecha) VALUES (%s, %s, %s)",
                (nombre_archivo, ruta_archivo, fecha)
            )
            self.conn.commit()
            cursor.close()
            print("Documento insertado exitosamente.")
        except ValueError:
            print("Error: Formato de fecha no válido. Use DD/MM/YYYY.")
        except psycopg2.Error as e:
            print("Error al insertar documento:", e)
            self.conn.rollback()

    def insertar_log(self, estado, tipo_error):
        """Inserta un documento en la tabla documentos."""
        if not self.conn:
            print("Conexión no disponible.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO logs (estado, tipo_error) VALUES (%s, %s)",
                (estado, tipo_error)
            )
            self.conn.commit()
            cursor.close()
            print("Log insertado exitosamente.")
        except psycopg2.Error as e:
            print("Error al insertar Log:", e)
            self.conn.rollback()

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            print("Conexión cerrada.")