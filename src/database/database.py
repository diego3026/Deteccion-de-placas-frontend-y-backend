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

    def obtener_informes(self):
        """Obtiene todos los informes de la tabla documentos como una lista."""
        if not self.conn:
            print("Conexión no disponible.")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM documentos")
            informes = cursor.fetchall()  # Obtiene todos los registros
            cursor.close()
            return informes
        except psycopg2.Error as e:
            print("Error al obtener informes:", e)
            return []
        
    def obtener_logs(self):
        """Obtiene todos los logs de la tabla logs como una lista."""
        if not self.conn:
            print("Conexión no disponible.")
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM logs")
            logs = cursor.fetchall()  # Obtiene todos los registros
            cursor.close()
            return logs
        except psycopg2.Error as e:
            print("Error al obtener logs:", e)
            return []

    def porcentaje_logs(self):
        """Calcula el porcentaje de registros con estado completado y no completado en la tabla logs."""
        if not self.conn:
            print("Conexión no disponible.")
            return {"COMPLETADO": 0, "INCOMPLETO": 0}

        try:
            cursor = self.conn.cursor()

            # Count total records in logs
            cursor.execute("SELECT COUNT(*) FROM logs")
            total_logs = cursor.fetchone()[0]

            if total_logs == 0:
                print("No hay registros en la tabla logs.")
                return {"COMPLETADO": 0, "INCOMPLETO": 0}

            # Count completed logs
            cursor.execute("SELECT COUNT(*) FROM logs WHERE estado = 'COMPLETADO'")
            completado_count = cursor.fetchone()[0]

            # Calculate percentages
            completado_percentage = (completado_count / total_logs) * 100
            incompleto_percentage = 100 - completado_percentage

            cursor.close()

            return {
                "COMPLETADO": completado_percentage,
                "INCOMPLETO": incompleto_percentage
            }
        except psycopg2.Error as e:
            print("Error al calcular porcentaje de logs:", e)
            return {"COMPLETADO": 0, "INCOMPLETO": 0}

    
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

    def insertar_vehiculo(self, placa, tipo_vehiculo, modelo, color):
        """Inserta un vehiculo en la tabla vehiculo."""
        if not self.conn:
            print("Conexión no disponible.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO vehiculos (placa, tipo_vehiculo, modelo, color) VALUES (%s, %s, %s, %s, %s)",
                (placa, tipo_vehiculo, modelo, color)
            )
            self.conn.commit()
            cursor.close()
            print("Vehiculo insertado exitosamente.")
        except psycopg2.Error as e:
            print("Error al insertar vehiculo:", e)
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

db = Database(dbname="your_db", user="your_user", password="your_password")
