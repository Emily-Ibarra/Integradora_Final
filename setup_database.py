import mysql.connector
from mysql.connector import Error
import hashlib

DB_CONFIG = {"host": "localhost", "user": "root", "password": ""}
DB_NAME = "restaurante_pro_db"

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Reiniciar Base de Datos
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4")
        cursor.execute(f"USE {DB_NAME}")

        # --- TABLA 1: USUARIOS ---
        cursor.execute("""
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                rol VARCHAR(50) NOT NULL
            )
        """)

        # --- TABLA 2: MESAS ---
        
        cursor.execute("""
            CREATE TABLE mesas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero VARCHAR(10) NOT NULL UNIQUE,
                estado VARCHAR(20) DEFAULT 'Libre'
            )
        """)

        # --- TABLA 3: MENU ---
        cursor.execute("""
            CREATE TABLE menu (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                activo TINYINT DEFAULT 1
            )
        """)

        # --- TABLA 4: PEDIDOS (La Cabecera) ---
        # Conecta con USUARIOS y MESAS
        cursor.execute("""
            CREATE TABLE pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(100),
                id_mesa INT, 
                id_usuario INT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2) DEFAULT 0,
                estado VARCHAR(50) DEFAULT 'Pendiente',
                FOREIGN KEY (id_mesa) REFERENCES mesas(id),
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            )
        """)

        # --- TABLA 5: DETALLE_PEDIDO (El contenido) ---
        # Conecta PEDIDOS con MENU. Aquí ocurre la magia relacional.
        cursor.execute("""
            CREATE TABLE detalle_pedido (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_pedido INT,
                id_producto INT,
                cantidad INT,
                precio_unitario DECIMAL(10,2),
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE CASCADE,
                FOREIGN KEY (id_producto) REFERENCES menu(id)
            )
        """)

        # --- DATOS DE PRUEBA ---

        # Usuarios
        users = [
            ("Admin", "admin@correo.com", "admin123", "admin"),
            ("Mesero 1", "mesero@correo.com", "mesero123", "mesero"),
            ("Chef", "cocina@correo.com", "cocina123", "cocina")
        ]
        for n, e, p, r in users:
            cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)", (n,e,hash_pass(p),r))

        
        for i in range(1, 11):
            cursor.execute("INSERT INTO mesas (numero) VALUES (%s)", (str(i),))

        # Menú
        items = [
            ("Gordita - ASADO ROJO", "Gorditas", 21.00),
            ("Gordita - ASADO VERDE", "Gorditas", 21.00),
            ("Gordita - DESHEBRADA", "Gorditas", 21.00),
            ("Gordita - CHICHARRON", "Gorditas", 21.00),
            ("Burro - ASADO ROJO", "Burros", 36.00),
            ("Burro - DESHEBRADA", "Burros", 36.00),
            ("Carnitas (kg)", "Kilos", 320.00),
            ("Coca Cola", "Bebidas", 25.00),
            ("Guacamole", "Extras", 35.00)
        ]
        cursor.executemany("INSERT INTO menu (nombre, categoria, precio) VALUES (%s, %s, %s)", items)

        conn.commit()
        print("✅ Base de Datos correctamente.")

    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    setup()