"""
Capa de acceso a datos para Villa Marina.
"""
import sqlite3
import hashlib
import secrets
from datetime import date, datetime
from contextlib import contextmanager

DB_PATH = "villa_marina.db"

INVENTARIO_INICIAL = {
    "Pollo (Cuartos)": {"categoria": "Carnes", "stock": 266.0, "unidad": "cuartos", "precio_usd": 3.50, "codigo_barras": ""},
    "Chorizo Artesanal": {"categoria": "Carnes", "stock": 44.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
    "Carne de Res (Congelada)": {"categoria": "Carnes", "stock": 7725.0, "unidad": "gramos (g)", "precio_usd": 0.008, "codigo_barras": ""},
    "Carne de Cerdo (Congelada)": {"categoria": "Carnes", "stock": 5530.0, "unidad": "gramos (g)", "precio_usd": 0.007, "codigo_barras": ""},
    "Carne de Ovejo (Congelada)": {"categoria": "Carnes", "stock": 2500.0, "unidad": "gramos (g)", "precio_usd": 0.009, "codigo_barras": ""},
    "Papas Fritas (Porción)": {"categoria": "Guarniciones", "stock": 20.0, "unidad": "porciones", "precio_usd": 2.50, "codigo_barras": ""},
    "Yuca Fresca": {"categoria": "Guarniciones", "stock": 7980.0, "unidad": "gramos (g)", "precio_usd": 0.005, "codigo_barras": ""},
    "Queso": {"categoria": "Insumos", "stock": 2000.0, "unidad": "gramos (g)", "precio_usd": 0.01, "codigo_barras": ""},
    "Mayonesa/Salsa": {"categoria": "Insumos", "stock": 1000.0, "unidad": "gramos (g)", "precio_usd": 0.01, "codigo_barras": ""},
    "Sopa": {"categoria": "Comida", "stock": 50.0, "unidad": "porciones", "precio_usd": 3.00, "codigo_barras": ""},
    "Pulpa de Mora": {"categoria": "Pulpas", "stock": 12.0, "unidad": "porciones", "precio_usd": 1.20, "codigo_barras": ""},
    "Pulpa de Piña": {"categoria": "Pulpas", "stock": 6.0, "unidad": "porciones", "precio_usd": 1.00, "codigo_barras": ""},
    "Pulpa de Guanábana": {"categoria": "Pulpas", "stock": 17.0, "unidad": "porciones", "precio_usd": 1.50, "codigo_barras": ""},
    "Bandejas de Aluminio (Llevar)": {"categoria": "Empaques", "stock": 100.0, "unidad": "unidades", "precio_usd": 0.50, "codigo_barras": ""},
    "Vasos (Medida 57)": {"categoria": "Empaques", "stock": 100.0, "unidad": "unidades", "precio_usd": 0.15, "codigo_barras": ""},
    "Galletas Oreo": {"categoria": "Chucherías", "stock": 7.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": "7591000333444"},
    "Doritos (Grande)": {"categoria": "Chucherías", "stock": 8.0, "unidad": "unidades", "precio_usd": 3.00, "codigo_barras": "7591000555666"},
    "Refresco (1.5 Litros)": {"categoria": "Bebidas", "stock": 108.0, "unidad": "unidades", "precio_usd": 3.00, "codigo_barras": "7591000111222"},
    "Refresco (350 ml)": {"categoria": "Bebidas", "stock": 53.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
    "Cerveza": {"categoria": "Bebidas", "stock": 14.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": "7591000777888"},
}

# Diccionario inicial de recetas para migrar a la base de datos la primera vez.
RECETAS_INICIALES = {
    "Jugo de Mora": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Mora": 1.0, "Vasos (Medida 57)": 1.0}},
    "Jugo de Piña": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Piña": 1.0, "Vasos (Medida 57)": 1.0}},
    "Pollo Entero (Crudo, para llevar)": {"categoria": "Aves", "precio_usd": 6.50, "ingredientes": {"Pollo (Cuartos)": 4.0}},
    "Parrilla de Muslos de Pollo": {"categoria": "Parrilla Personal", "precio_usd": 7.00, "ingredientes": {"Pollo (Cuartos)": 1.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Pechuga de Pollo": {"categoria": "Parrilla Personal", "precio_usd": 7.00, "ingredientes": {"Pollo (Cuartos)": 1.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Carne de Res": {"categoria": "Parrilla Personal", "precio_usd": 9.00, "ingredientes": {"Carne de Res (Congelada)": 330.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Pistolitas de Cerdo": {"categoria": "Parrilla Personal", "precio_usd": 8.00, "ingredientes": {"Carne de Cerdo (Congelada)": 330.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Costilla de Cerdo": {"categoria": "Parrilla Personal", "precio_usd": 8.00, "ingredientes": {"Carne de Cerdo (Congelada)": 330.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Chorizo": {"categoria": "Parrilla Personal", "precio_usd": 7.00, "ingredientes": {"Chorizo Artesanal": 3.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Ovejo": {"categoria": "Parrilla Personal", "precio_usd": 7.00, "ingredientes": {"Carne de Ovejo (Congelada)": 330.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Pollo (2) Personas": {"categoria": "Parrilla Familiar", "precio_usd": 14.00, "ingredientes": {"Pollo (Cuartos)": 2.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Parrilla de Carne de Res (2) Personas": {"categoria": "Parrilla Familiar", "precio_usd": 18.00, "ingredientes": {"Carne de Res (Congelada)": 660.0, "Bandejas de Aluminio (Llevar)": 1.0}},
    "Papas Fritas 250 gr": {"categoria": "Servicios Adicionales", "precio_usd": 2.50, "ingredientes": {"Papas Fritas (Porción)": 1.0}},
    "Yuca 350gr": {"categoria": "Servicios Adicionales", "precio_usd": 2.00, "ingredientes": {"Yuca Fresca": 350.0}},
    "Queso 200gr": {"categoria": "Servicios Adicionales", "precio_usd": 2.00, "ingredientes": {"Queso": 200.0}},
}

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL CHECK(rol IN ('admin','supervisor','vendedor')),
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS inventario (
                item TEXT PRIMARY KEY,
                categoria TEXT NOT NULL,
                stock REAL NOT NULL,
                unidad TEXT NOT NULL,
                precio_usd REAL NOT NULL,
                codigo_barras TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS recetas (
                nombre TEXT PRIMARY KEY,
                categoria TEXT NOT NULL,
                precio_usd REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS receta_ingredientes (
                receta_nombre TEXT NOT NULL,
                ingrediente TEXT NOT NULL,
                cantidad REAL NOT NULL,
                FOREIGN KEY(receta_nombre) REFERENCES recetas(nombre) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                vendedor TEXT NOT NULL,
                pedido TEXT NOT NULL,
                monto REAL NOT NULL,
                metodo TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS totales (
                fecha TEXT NOT NULL,
                metodo TEXT NOT NULL,
                monto REAL NOT NULL DEFAULT 0,
                PRIMARY KEY (fecha, metodo)
            );
            CREATE TABLE IF NOT EXISTS estadisticas_items (
                fecha TEXT NOT NULL,
                item TEXT NOT NULL,
                cantidad REAL NOT NULL DEFAULT 0,
                PRIMARY KEY (fecha, item)
            );
            CREATE TABLE IF NOT EXISTS auditoria_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                usuario TEXT NOT NULL,
                item TEXT NOT NULL,
                delta REAL NOT NULL,
                motivo TEXT NOT NULL
            );
            """
        )
        
        # Siembra de inventario inicial
        ya_sembrado = conn.execute("SELECT COUNT(*) AS n FROM inventario").fetchone()["n"]
        if ya_sembrado == 0:
            for item, datos in INVENTARIO_INICIAL.items():
                conn.execute(
                    "INSERT INTO inventario (item, categoria, stock, unidad, precio_usd, codigo_barras) VALUES (?,?,?,?,?,?)",
                    (item, datos["categoria"], datos["stock"], datos["unidad"], datos["precio_usd"], datos["codigo_barras"]),
                )
                
        # Siembra de recetas iniciales
        ya_recetas = conn.execute("SELECT COUNT(*) AS n FROM recetas").fetchone()["n"]
        if ya_recetas == 0:
            for nombre, datos in RECETAS_INICIALES.items():
                conn.execute("INSERT INTO recetas (nombre, categoria, precio_usd) VALUES (?,?,?)", (nombre, datos["categoria"], datos["precio_usd"]))
                for ing, cant in datos["ingredientes"].items():
                    conn.execute("INSERT INTO receta_ingredientes (receta_nombre, ingrediente, cantidad) VALUES (?,?,?)", (nombre, ing, cant))
                    
        _migrar_pollo_fraccionado(conn)
        _migrar_items_faltantes(conn)

def _migrar_pollo_fraccionado(conn):
    ya_migrado = conn.execute("SELECT 1 FROM inventario WHERE item='Pollo (Cuartos)'").fetchone()
    fila_entero = conn.execute("SELECT * FROM inventario WHERE item='Pollo Entero'").fetchone()
    fila_cuarto = conn.execute("SELECT * FROM inventario WHERE item='Porción de Pollo (1 Cuarto)'").fetchone()
    if ya_migrado or (not fila_entero and not fila_cuarto): return

    cuartos_totales = 0.0
    precio = 3.50
    if fila_entero: cuartos_totales += fila_entero["stock"] * 4.0
    if fila_cuarto:
        cuartos_totales += fila_cuarto["stock"]
        precio = fila_cuarto["precio_usd"] or precio

    conn.execute("INSERT INTO inventario (item, categoria, stock, unidad, precio_usd, codigo_barras) VALUES (?,?,?,?,?,?)", ("Pollo (Cuartos)", "Carnes", cuartos_totales, "cuartos", precio, ""))
    conn.execute("DELETE FROM inventario WHERE item IN ('Pollo Entero', 'Porción de Pollo (1 Cuarto)')")
    conn.execute("INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), "sistema", "Pollo (Cuartos)", cuartos_totales, "migración automática: unificación de 'Pollo Entero' + 'Porción de Pollo (1 Cuarto)' en inventario por cuartos"))

ITEMS_FALTANTES = {
    "Agua 600ml": {"categoria": "Bebidas", "stock": 0.0, "unidad": "unidades", "precio_usd": 1.5, "codigo_barras": ""},
    "Café": {"categoria": "Bebidas", "stock": 0.0, "unidad": "unidades", "precio_usd": 1.05, "codigo_barras": ""},
    "Tip Top": {"categoria": "Chucherías", "stock": 0.0, "unidad": "unidades", "precio_usd": 1.5, "codigo_barras": ""},
}

def _migrar_items_faltantes(conn):
    for item, datos in ITEMS_FALTANTES.items():
        existe = conn.execute("SELECT 1 FROM inventario WHERE item=?", (item,)).fetchone()
        if not existe:
            conn.execute("INSERT INTO inventario (item, categoria, stock, unidad, precio_usd, codigo_barras) VALUES (?,?,?,?,?,?)", (item, datos["categoria"], datos["stock"], datos["unidad"], datos["precio_usd"], datos["codigo_barras"]))

# ---------------- Autenticación ----------------
def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()

def crear_o_actualizar_usuario(username: str, nombre: str, rol: str, password: str):
    username = username.strip().lower()
    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    with get_connection() as conn:
        conn.execute("INSERT INTO usuarios (username, nombre, rol, password_hash, salt) VALUES (?,?,?,?,?) ON CONFLICT(username) DO UPDATE SET nombre=excluded.nombre, rol=excluded.rol, password_hash=excluded.password_hash, salt=excluded.salt", (username, nombre, rol, pw_hash, salt))

def verificar_credenciales(username: str, password: str):
    username = username.strip().lower()
    with get_connection() as conn:
        fila = conn.execute("SELECT * FROM usuarios WHERE username=?", (username,)).fetchone()
    if not fila: return None
    pw_hash = _hash_password(password, fila["salt"])
    if secrets.compare_digest(pw_hash, fila["password_hash"]):
        return {"username": fila["username"], "nombre": fila["nombre"], "rol": fila["rol"]}
    return None

def hay_usuarios() -> bool:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"] > 0

# ---------------- Inventario ----------------
def obtener_inventario() -> dict:
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM inventario").fetchall()
    return {f["item"]: dict(f) for f in filas}

def ajustar_stock(item: str, delta: float, usuario: str, motivo: str = "ajuste manual"):
    with get_connection() as conn:
        conn.execute("UPDATE inventario SET stock = stock + ? WHERE item = ?", (delta, item))
        conn.execute("INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), usuario, item, delta, motivo))

def fijar_stock(item: str, nuevo_stock: float, usuario: str, motivo: str = "conteo físico"):
    with get_connection() as conn:
        fila = conn.execute("SELECT stock FROM inventario WHERE item=?", (item,)).fetchone()
        if fila is None: raise ValueError(f"El ítem '{item}' no existe en el inventario.")
        anterior = fila["stock"]
        delta = nuevo_stock - anterior
        conn.execute("UPDATE inventario SET stock = ? WHERE item = ?", (nuevo_stock, item))
        conn.execute("INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), usuario, item, delta, f"{motivo} (antes: {anterior})"))

def agregar_item(item: str, categoria: str, stock: float, unidad: str, precio_usd: float, codigo_barras: str = ""):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO inventario (item, categoria, stock, unidad, precio_usd, codigo_barras) VALUES (?,?,?,?,?,?)", (item, categoria, stock, unidad, precio_usd, codigo_barras))

def actualizar_precio(item: str, nuevo_precio: float, usuario: str):
    with get_connection() as conn:
        anterior = conn.execute("SELECT precio_usd FROM inventario WHERE item=?", (item,)).fetchone()
        precio_anterior = anterior["precio_usd"] if anterior else None
        conn.execute("UPDATE inventario SET precio_usd = ? WHERE item = ?", (nuevo_precio, item))
        conn.execute("INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), usuario, item, 0.0, f"cambio de precio: {precio_anterior} -> {nuevo_precio} USD"))

def descontar_stock_por_venta(requerimientos: dict, usuario: str):
    with get_connection() as conn:
        actuales = {r["item"]: r["stock"] for r in conn.execute("SELECT item, stock FROM inventario")}
        faltantes = [k for k, v in requerimientos.items() if actuales.get(k, 0) < v]
        if faltantes: raise ValueError("Stock insuficiente en: " + ", ".join(faltantes))
        for item, cant in requerimientos.items():
            conn.execute("UPDATE inventario SET stock = stock - ? WHERE item = ?", (cant, item))
            conn.execute("INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), usuario, item, -cant, "venta"))

def obtener_auditoria(limite: int = 100):
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM auditoria_stock ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
    return [dict(f) for f in filas]

# ---------------- Recetas y Menú (Nuevo Módulo) ----------------
def obtener_recetas() -> dict:
    with get_connection() as conn:
        filas_r = conn.execute("SELECT * FROM recetas").fetchall()
        recetas = {r["nombre"]: {"categoria": r["categoria"], "precio_usd": r["precio_usd"], "ingredientes": {}} for r in filas_r}
        filas_i = conn.execute("SELECT * FROM receta_ingredientes").fetchall()
        for i in filas_i:
            if i["receta_nombre"] in recetas:
                recetas[i["receta_nombre"]]["ingredientes"][i["ingrediente"]] = i["cantidad"]
    return recetas

def guardar_receta(nombre: str, categoria: str, precio_usd: float, ingredientes: dict):
    with get_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO recetas (nombre, categoria, precio_usd) VALUES (?,?,?)", (nombre, categoria, precio_usd))
        conn.execute("DELETE FROM receta_ingredientes WHERE receta_nombre=?", (nombre,))
        for ing, cant in ingredientes.items():
            conn.execute("INSERT INTO receta_ingredientes (receta_nombre, ingrediente, cantidad) VALUES (?,?,?)", (nombre, ing, cant))

def eliminar_receta(nombre: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM recetas WHERE nombre=?", (nombre,))

# ---------------- Ventas / totales / estadísticas (por día) ----------------
def registrar_venta(vendedor: str, pedido: str, monto: float, metodo: str, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute("INSERT INTO ventas (fecha, hora, vendedor, pedido, monto, metodo) VALUES (?,?,?,?,?,?)", (fecha, datetime.now().strftime("%I:%M %p"), vendedor, pedido, monto, metodo))

def sumar_total(metodo: str, monto: float, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute("INSERT INTO totales (fecha, metodo, monto) VALUES (?,?,?) ON CONFLICT(fecha, metodo) DO UPDATE SET monto = monto + excluded.monto", (fecha, metodo, monto))

def sumar_item_vendido(item: str, cantidad: float, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute("INSERT INTO estadisticas_items (fecha, item, cantidad) VALUES (?,?,?) ON CONFLICT(fecha, item) DO UPDATE SET cantidad = cantidad + excluded.cantidad", (fecha, item, cantidad))

def obtener_ventas(fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM ventas WHERE fecha=? ORDER BY id", (fecha,)).fetchall()
    return [dict(f) for f in filas]

def obtener_totales(fecha: str = None) -> dict:
    fecha = fecha or date.today().isoformat()
    totales = {"Digital": 0.0, "Bs": 0.0, "USD": 0.0}
    with get_connection() as conn:
        for f in conn.execute("SELECT metodo, monto FROM totales WHERE fecha=?", (fecha,)):
            totales[f["metodo"]] = f["monto"]
    return totales

def obtener_estadisticas(fecha: str = None) -> dict:
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        filas = conn.execute("SELECT item, cantidad FROM estadisticas_items WHERE fecha=?", (fecha,)).fetchall()
    return {f["item"]: f["cantidad"] for f in filas}