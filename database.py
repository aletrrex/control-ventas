"""
Capa de acceso a datos para Villa Marina.

Toda la información compartida (usuarios, inventario, ventas, estadísticas,
auditoría) vive en un único archivo SQLite: villa_marina.db, en la misma
carpeta que este archivo. Así, sin importar desde qué dispositivo o
navegador entre cada vendedor, todos leen y escriben los mismos datos
(a diferencia de guardar todo en st.session_state, que es por sesión).
"""
import sqlite3
import hashlib
import secrets
from datetime import date, datetime
from contextlib import contextmanager

DB_PATH = "villa_marina.db"

# Inventario inicial: solo se usa la primera vez que se crea la base de datos.
# Después de esto, todos los cambios de stock se hacen desde la app y quedan
# guardados en villa_marina.db, no aquí.
INVENTARIO_INICIAL = {
    "Pollo Entero": {"categoria": "Carnes", "stock": 59.0, "unidad": "unidades", "precio_usd": 6.50, "codigo_barras": ""},
    "Porción de Pollo (1 Cuarto)": {"categoria": "Carnes", "stock": 30.0, "unidad": "piezas", "precio_usd": 3.50, "codigo_barras": ""},
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


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Crea las tablas si no existen y siembra el inventario inicial una sola vez."""
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
        ya_sembrado = conn.execute("SELECT COUNT(*) AS n FROM inventario").fetchone()["n"]
        if ya_sembrado == 0:
            for item, datos in INVENTARIO_INICIAL.items():
                conn.execute(
                    "INSERT INTO inventario (item, categoria, stock, unidad, precio_usd, codigo_barras) "
                    "VALUES (?,?,?,?,?,?)",
                    (item, datos["categoria"], datos["stock"], datos["unidad"], datos["precio_usd"], datos["codigo_barras"]),
                )


# ---------------- Autenticación ----------------
def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()


def crear_o_actualizar_usuario(username: str, nombre: str, rol: str, password: str):
    username = username.strip().lower()
    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO usuarios (username, nombre, rol, password_hash, salt) VALUES (?,?,?,?,?) "
            "ON CONFLICT(username) DO UPDATE SET nombre=excluded.nombre, rol=excluded.rol, "
            "password_hash=excluded.password_hash, salt=excluded.salt",
            (username, nombre, rol, pw_hash, salt),
        )


def verificar_credenciales(username: str, password: str):
    """Devuelve {'username','nombre','rol'} si son correctas, o None si no."""
    username = username.strip().lower()
    with get_connection() as conn:
        fila = conn.execute("SELECT * FROM usuarios WHERE username=?", (username,)).fetchone()
    if not fila:
        return None
    pw_hash = _hash_password(password, fila["salt"])
    if secrets.compare_digest(pw_hash, fila["password_hash"]):
        return {"username": fila["username"], "nombre": fila["nombre"], "rol": fila["rol"]}
    return None


def hay_usuarios() -> bool:
    with get_connection() as conn:
        n = conn.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
    return n > 0


# ---------------- Inventario ----------------
def obtener_inventario() -> dict:
    with get_connection() as conn:
        filas = conn.execute("SELECT * FROM inventario").fetchall()
    return {f["item"]: dict(f) for f in filas}


def ajustar_stock(item: str, delta: float, usuario: str, motivo: str = "ajuste manual"):
    with get_connection() as conn:
        conn.execute("UPDATE inventario SET stock = stock + ? WHERE item = ?", (delta, item))
        conn.execute(
            "INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), usuario, item, delta, motivo),
        )


def descontar_stock_por_venta(requerimientos: dict, usuario: str):
    """requerimientos: {item: cantidad_a_descontar}. Lanza ValueError si falta stock."""
    with get_connection() as conn:
        actuales = {r["item"]: r["stock"] for r in conn.execute("SELECT item, stock FROM inventario")}
        faltantes = [k for k, v in requerimientos.items() if actuales.get(k, 0) < v]
        if faltantes:
            raise ValueError("Stock insuficiente en: " + ", ".join(faltantes))
        for item, cant in requerimientos.items():
            conn.execute("UPDATE inventario SET stock = stock - ? WHERE item = ?", (cant, item))
            conn.execute(
                "INSERT INTO auditoria_stock (fecha_hora, usuario, item, delta, motivo) VALUES (?,?,?,?,?)",
                (datetime.now().isoformat(timespec="seconds"), usuario, item, -cant, "venta"),
            )


def obtener_auditoria(limite: int = 100):
    with get_connection() as conn:
        filas = conn.execute(
            "SELECT * FROM auditoria_stock ORDER BY id DESC LIMIT ?", (limite,)
        ).fetchall()
    return [dict(f) for f in filas]


# ---------------- Ventas / totales / estadísticas (por día) ----------------
def registrar_venta(vendedor: str, pedido: str, monto: float, metodo: str, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO ventas (fecha, hora, vendedor, pedido, monto, metodo) VALUES (?,?,?,?,?,?)",
            (fecha, datetime.now().strftime("%I:%M %p"), vendedor, pedido, monto, metodo),
        )


def sumar_total(metodo: str, monto: float, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO totales (fecha, metodo, monto) VALUES (?,?,?) "
            "ON CONFLICT(fecha, metodo) DO UPDATE SET monto = monto + excluded.monto",
            (fecha, metodo, monto),
        )


def sumar_item_vendido(item: str, cantidad: float, fecha: str = None):
    fecha = fecha or date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO estadisticas_items (fecha, item, cantidad) VALUES (?,?,?) "
            "ON CONFLICT(fecha, item) DO UPDATE SET cantidad = cantidad + excluded.cantidad",
            (fecha, item, cantidad),
        )


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
        filas = conn.execute(
            "SELECT item, cantidad FROM estadisticas_items WHERE fecha=?", (fecha,)
        ).fetchall()
    return {f["item"]: f["cantidad"] for f in filas}
