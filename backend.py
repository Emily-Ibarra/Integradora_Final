import mysql.connector
import hashlib
import pandas as pd
from tkinter import filedialog

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "", 
    "database": "restaurante_pro_db", "auth_plugin": "mysql_native_password"
}

def get_conn():
    try: return mysql.connector.connect(**DB_CONFIG)
    except Exception as e: print(e); return None

# USUARIOS
def login(email, password):
    conn = get_conn()
    if not conn: return None
    try:
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, pwd_hash))
        return cursor.fetchone()
    finally:
        conn.close()

def crear_usuario(nombre, email, password, rol):
    conn = get_conn()
    if not conn: return False
    try:
        cursor = conn.cursor()
        pwd = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s,%s,%s,%s)", 
                       (nombre, email, pwd, rol))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# MENU
def get_menu(filtro=""):
    conn = get_conn()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM menu WHERE activo=1"
        if filtro:
            sql += f" AND (nombre LIKE '%{filtro}%' OR categoria LIKE '%{filtro}%')"
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()

def agregar_producto(nombre, categoria, precio):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (nombre, categoria, precio) VALUES (%s,%s,%s)", (nombre, categoria, precio))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# PEDIDOS RELACIONALES 
def guardar_pedido(cliente, mesa_num, items, total, id_user, id_pedido=None):
    conn = get_conn()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT id FROM mesas WHERE numero=%s", (mesa_num,))
        res = cursor.fetchone()
        if res:
            mesa_id = res[0]
            
            cursor.execute("UPDATE mesas SET estado='Ocupada' WHERE id=%s", (mesa_id,))
        else:
            
            cursor.execute("INSERT INTO mesas (numero, estado) VALUES (%s, 'Ocupada')", (mesa_num,))
            mesa_id = cursor.lastrowid

        
        if id_pedido:
            
            cursor.execute("""
                UPDATE pedidos SET cliente=%s, id_mesa=%s, total=%s, estado='Pendiente' 
                WHERE id=%s
            """, (cliente, mesa_id, total, id_pedido))
            current_id = id_pedido
            
            cursor.execute("DELETE FROM detalle_pedido WHERE id_pedido=%s", (id_pedido,))
        else:
           
            cursor.execute("""
                INSERT INTO pedidos (cliente, id_mesa, id_usuario, total, estado) 
                VALUES (%s, %s, %s, %s, 'Pendiente')
            """, (cliente, mesa_id, id_user, total))
            current_id = cursor.lastrowid

        
        for item in items:
            # Obtenemos ID del producto del menú
            cursor.execute("SELECT id FROM menu WHERE nombre=%s", (item['nombre'],))
            prod = cursor.fetchone()
            if prod:
                prod_id = prod[0]
                # Insertamos en la tabla relacional
                cursor.execute("""
                    INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (current_id, prod_id, item['cantidad'], item['precio']))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error Transacción: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def obtener_pedidos(filtro_estado=None, busqueda=""):
    conn = get_conn()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener lista de pedidos (JOIN con Mesas y Usuarios)
        sql = """
            SELECT p.id, p.fecha, p.cliente, m.numero as mesa, u.nombre as mesero, p.total, p.estado
            FROM pedidos p
            JOIN mesas m ON p.id_mesa = m.id
            LEFT JOIN usuarios u ON p.id_usuario = u.id
        """
        conds = []
        if filtro_estado == "cocina": conds.append("p.estado IN ('Pendiente', 'En Preparacion')")
        if busqueda: conds.append(f"(p.cliente LIKE '%{busqueda}%' OR m.numero LIKE '%{busqueda}%')")
        
        if conds: sql += " WHERE " + " AND ".join(conds)
        
        if filtro_estado == "cocina": sql += " ORDER BY p.fecha ASC"
        else: sql += " ORDER BY p.fecha DESC"
        
        cursor.execute(sql)
        pedidos = cursor.fetchall()
        
        # 2. Llenar los detalles de cada pedido (Consultando tabla detalle_pedido)
        for p in pedidos:
            p['total'] = float(p['total']) # Corrección decimal
            
            # Subconsulta relacional para traer los items de este pedido específico
            cursor.execute("""
                SELECT d.cantidad, mn.nombre, d.precio_unitario as precio
                FROM detalle_pedido d
                JOIN menu mn ON d.id_producto = mn.id
                WHERE d.id_pedido = %s
            """, (p['id'],))
            
            items_db = cursor.fetchall()
            
            # Reconstruimos formato lista para que la UI lo entienda
            p['items'] = []
            for it in items_db:
                p['items'].append({
                    "nombre": it['nombre'],
                    "cantidad": it['cantidad'],
                    "precio": float(it['precio'])
                })

        return pedidos
    finally:
        conn.close()

def cambiar_estado(id_pedido, nuevo_estado):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE pedidos SET estado=%s WHERE id=%s", (nuevo_estado, id_pedido))
        
        # Si el pedido se termina o cancela, liberamos la mesa
        if nuevo_estado in ['Entregado', 'Cancelado']:
            cursor.execute("SELECT id_mesa FROM pedidos WHERE id=%s", (id_pedido,))
            res = cursor.fetchone()
            if res:
                cursor.execute("UPDATE mesas SET estado='Libre' WHERE id=%s", (res[0],))
                
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def eliminar_pedido(id_pedido):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        # Liberar mesa antes de borrar
        cursor.execute("SELECT id_mesa FROM pedidos WHERE id=%s", (id_pedido,))
        res = cursor.fetchone()
        if res:
            cursor.execute("UPDATE mesas SET estado='Libre' WHERE id=%s", (res[0],))
        
        cursor.execute("DELETE FROM pedidos WHERE id=%s", (id_pedido,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def exportar_excel():
    conn = get_conn()
    try:
        
        query = """
            SELECT p.id, p.fecha, p.cliente, m.numero as mesa, u.nombre as mesero, p.total, p.estado
            FROM pedidos p
            JOIN mesas m ON p.id_mesa = m.id
            LEFT JOIN usuarios u ON p.id_usuario = u.id
        """
        df = pd.read_sql(query, conn)
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if filename:
            df.to_excel(filename, index=False)
            return True
    except Exception as e:
        print(f"Error Excel: {e}")
        return False
    finally:
        conn.close()
    return False