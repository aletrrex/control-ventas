import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página web
st.set_page_config(page_title="Control de Ventas e Inventario", page_icon="🛒", layout="centered")

# --- BASE DE DATOS EN MEMORIA / SESIÓN (Ideal para conectar a Google Sheets después) ---
if "inventario" not in st.session_state:
    st.session_state.inventario = {"Harina": 50, "Arroz": 30, "Aceite": 20}

if "ventas" not in st.session_state:
    st.session_state.ventas = []

if "totales" not in st.session_state:
    st.session_state.totales = {"Digital": 0.0, "Bs": 0.0, "USD": 0.0}

# --- SISTEMA DE USUARIOS Y CONTRASEÑAS ---
CREDENCIALES = {
    "alejandro": {"pass": "admin2026", "nombre": "Alejandro (Admin)", "rol": "admin"},
    "janet": {"pass": "tiajanet123", "nombre": "Tía Janet (Tienda)", "rol": "vendedor"},
    "jackeline": {"pass": "tiajack123", "nombre": "Tía Jackeline (EE.UU.)", "rol": "supervisor"}
}

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

# Pantalla de Login si no ha iniciado sesión
if not st.session_state.usuario_actual:
    st.title("🔐 Acceso al Sistema - Control de Ventas")
    st.markdown("Por favor ingresa tus credenciales asignadas.")
    
    user_input = st.text_input("Usuario:")
    pass_input = st.text_input("Contraseña:", type="password")
    
    if st.button("Iniciar Sesión", type="primary"):
        user_lower = user_input.strip().lower()
        if user_lower in CREDENCIALES and CREDENCIALES[user_lower]["pass"] == pass_input:
            st.session_state.usuario_actual = CREDENCIALES[user_lower]
            st.success(f"¡Bienvenido, {st.session_state.usuario_actual['nombre']}!")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop() # Detiene la ejecución aquí hasta que se loguee

# --- PANTALLA PRINCIPAL (Una vez dentro) ---
usuario = st.session_state.usuario_actual
st.sidebar.markdown(f"👤 **Conectado como:** {usuario['nombre']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.title("🛒 Control de Ventas e Inventario")

# Menú lateral adaptado por roles
opciones_menu = ["Control de Ventas", "Ver Inventario"]
if usuario["rol"] == "admin":
    opciones_menu.extend(["Gestión de Inventario (Admin)", "Cierre Diario"])
elif usuario["rol"] == "supervisor":
    opciones_menu.append("Cierre Diario")

menu = st.sidebar.selectbox("Menú de Navegación", opciones_menu)

# ==========================================
# 1. CONTROL DE VENTAS
# ==========================================
if menu == "Control de Ventas":
    st.header("Registrar Venta")
    
    tasa = st.number_input("Tasa de Cambio del Día (Bs/$):", min_value=0.0, value=36.50, format="%.2f")
    
    productos_disponibles = list(st.session_state.inventario.keys())
    
    if not productos_disponibles:
        st.warning("⚠️ No hay productos en el inventario.")
    else:
        prod_sel = st.selectbox("Producto vendido:", productos_disponibles)
        cantidad = st.number_input("Cantidad despachada:", min_value=0.0, value=1.0, format="%.2f")
        monto = st.number_input("Monto pagado:", min_value=0.0, value=0.0, format="%.2f")
        metodo = st.selectbox("Método de pago:", [
            "Digital (Pago Móvil / Punto)", 
            "Físico (Bolívares)", 
            "Físico (Dólares)"
        ])
        
        if st.button("Registrar Venta", type="primary"):
            if prod_sel and cantidad > 0 and monto > 0:
                stock_actual = st.session_state.inventario.get(prod_sel, 0)
                if stock_actual < cantidad:
                    st.warning(f"⚠️ Stock bajo. Quedan {stock_actual} unidades.")
                
                # Descontar inventario y sumar totales
                st.session_state.inventario[prod_sel] -= cantidad
                if metodo == "Digital (Pago Móvil / Punto)":
                    st.session_state.totales["Digital"] += monto
                elif metodo == "Físico (Bolívares)":
                    st.session_state.totales["Bs"] += monto
                elif metodo == "Físico (Dólares)":
                    st.session_state.totales["USD"] += monto
                
                st.session_state.ventas.append({
                    "hora": datetime.now().strftime('%I:%M %p'),
                    "usuario": usuario["nombre"],
                    "producto": prod_sel,
                    "cantidad": cantidad,
                    "monto": monto,
                    "metodo": metodo
                })
                st.success(f"✅ Venta de {prod_sel} registrada con éxito.")
            else:
                st.error("❌ Rellena todos los campos correctamente.")

# ==========================================
# 2. VER INVENTARIO
# ==========================================
elif menu == "Ver Inventario":
    st.header("📦 Inventario Actual en Stock")
    if st.session_state.inventario:
        df_inv = pd.DataFrame(list(st.session_state.inventario.items()), columns=["Producto", "Cantidad Disponible"])
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.info("El inventario está vacío.")

# ==========================================
# 3. GESTIÓN DE INVENTARIO (Solo Admin - Alejandro)
# ==========================================
elif menu == "Gestión de Inventario (Admin)":
    st.header("⚙️ Agregar o Modificar Stock")
    nuevo_prod = st.text_input("Nombre del Producto:")
    cant_nueva = st.number_input("Cantidad a agregar:", min_value=0.0, format="%.2f")
    
    if st.button("Guardar en Almacén"):
        if nuevo_prod.strip():
            st.session_state.inventario[nuevo_prod] = st.session_state.inventario.get(nuevo_prod, 0.0) + cant_nueva
            st.success(f"✅ Se agregaron {cant_nueva} unidades a '{nuevo_prod}'.")
        else:
            st.warning("Escribe un nombre válido.")

# ==========================================
# 4. CIERRE DIARIO (Admin y Supervisor)
# ==========================================
elif menu == "Cierre Diario":
    st.header("📊 Cierre de Caja y Reportes")
    tasa_cierre = st.number_input("Tasa aplicada para el cierre (Bs/$):", min_value=0.0, value=36.50, format="%.2f")
    
    if st.button("Calcular Cierre del Día", type="primary"):
        tot_dig = st.session_state.totales["Digital"]
        tot_bs = st.session_state.totales["Bs"]
        tot_usd = st.session_state.totales["USD"]
        
        bs_juntos = tot_dig + tot_bs
        eq_usd = bs_juntos / tasa_cierre if tasa_cierre > 0 else 0
        gran_total = tot_usd + eq_usd
        
        st.markdown(f"### 💵 Total Equivalente en Caja: {gran_total:.2f} $")
        col1, col2, col3 = st.columns(3)
        col1.metric("Digital (Bs)", f"{tot_dig:.2f} Bs")
        col2.metric("Efectivo (Bs)", f"{tot_bs:.2f} Bs")
        col3.metric("Efectivo ($)", f"{tot_usd:.2f} $")
        
        st.divider()
        st.subheader("📝 Historial de Ventas Registradas")
        if st.session_state.ventas:
            st.dataframe(pd.DataFrame(st.session_state.ventas), use_container_width=True)
        else:
            st.info("No hay ventas registradas en este turno.")