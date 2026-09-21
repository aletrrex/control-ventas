import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import json
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Control de Ventas - Villa Marina", 
    page_icon="🛒", 
    layout="centered",
    initial_sidebar_state="expanded"
)

def get_base64_image(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def load_lottiefile(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

bg_image_base64 = get_base64_image("assets/fondo_marino.jpg")
lottie_login = load_lottiefile("assets/animacion_login.json")
lottie_ventas = load_lottiefile("assets/animacion_ventas.json")
lottie_inventario = load_lottiefile("assets/animacion_inventario.json")
lottie_cierre = load_lottiefile("assets/animacion_cierre.json")

if bg_image_base64:
    bg_css = f"background-image: url('data:image/jpeg;base64,{bg_image_base64}'); background-size: cover; background-position: center; background-attachment: fixed;"
else:
    bg_css = "background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);"

st.markdown(f"""
<style>
    .stApp {{ {bg_css} color: #ffffff !important; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} 
    iframe {{ background-color: transparent !important; border: none !important; }}
    @keyframes fadeInFloat {{ 0% {{ opacity: 0; transform: translateY(30px); }} 100% {{ opacity: 1; transform: translateY(0px); }} }}
    @keyframes subtleBreathe {{ 0% {{ box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4); }} 50% {{ box-shadow: 0 12px 40px 0 rgba(0, 212, 255, 0.2); }} 100% {{ box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4); }} }}

    .block-container {{
        background: rgba(15, 32, 39, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 3rem 2rem !important;
        margin-top: 2rem !important;
        animation: fadeInFloat 1s ease-out forwards, subtleBreathe 6s infinite ease-in-out;
    }}
    [data-testid="stSidebar"] {{
        background: rgba(10, 25, 40, 0.3) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    h1, h2, h3, p, label, .stMarkdown {{ color: #ffffff !important; text-shadow: 0 2px 5px rgba(0,0,0,0.6); }}
    .stTextInput input, .stNumberInput input {{ background-color: rgba(255, 255, 255, 0.05) !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 12px !important; padding: 12px 16px !important; transition: all 0.4s !important; }}
    .stTextInput input:focus, .stNumberInput input:focus {{ border-color: #00d4ff !important; background-color: rgba(255, 255, 255, 0.15) !important; box-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 12px !important; }}
    .stButton > button {{ background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(5px) !important; color: #00d4ff !important; border-radius: 12px !important; border: 1px solid rgba(0, 212, 255, 0.3) !important; font-weight: 600 !important; padding: 10px 24px !important; transition: all 0.3s ease !important; width: 100%; text-transform: uppercase; letter-spacing: 1px; }}
    .stButton > button:hover {{ background: rgba(0, 212, 255, 0.2) !important; transform: translateY(-3px); border-color: #00d4ff !important; color: #ffffff !important; box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5) !important; }}
    [data-testid="stDataFrame"] {{ background: rgba(0, 0, 0, 0.3) !important; border-radius: 15px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }}
</style>
""", unsafe_allow_html=True)


if "inventario" not in st.session_state:
    st.session_state.inventario = {
        # --- CARNES (Materia Prima General) ---
        "Pollo Entero": {"categoria": "Carnes", "stock": 59.0, "unidad": "unidades"},
        "Nuggets de Pollo (Bandeja)": {"categoria": "Carnes", "stock": 3.0, "unidad": "bandejas"},
        "Chorizo Artesanal": {"categoria": "Carnes", "stock": 44.0, "unidad": "unidades"},
        "Carne de Res (Congelada)": {"categoria": "Carnes", "stock": 7725.0, "unidad": "gramos (g)"},
        "Carne de Cerdo (Congelada)": {"categoria": "Carnes", "stock": 5530.0, "unidad": "gramos (g)"},
        "Carne de Ovejo (Congelada)": {"categoria": "Carnes", "stock": 2500.0, "unidad": "gramos (g)"},
        "Papas Fritas (Bolsa Completa)": {"categoria": "Carnes", "stock": 2.0, "unidad": "bolsas"},
        "Papas Fritas (Porción)": {"categoria": "Carnes", "stock": 6.0, "unidad": "porciones"},

        # --- PULPAS DE FRUTAS ---
        "Pulpa de Piña": {"categoria": "Pulpas", "stock": 6.0, "unidad": "porciones"},
        "Pulpa de Mora": {"categoria": "Pulpas", "stock": 12.0, "unidad": "porciones"},
        "Pulpa de Guanábana": {"categoria": "Pulpas", "stock": 17.0, "unidad": "porciones"},
        "Pulpa de Durazno": {"categoria": "Pulpas", "stock": 13.0, "unidad": "porciones"},
        "Pulpa de Parchita": {"categoria": "Pulpas", "stock": 9.0, "unidad": "porciones"},
        "Pulpa de Fresa": {"categoria": "Pulpas", "stock": 12.0, "unidad": "porciones"},

        # --- GUARNICIONES ---
        "Yuca Fresca": {"categoria": "Guarniciones", "stock": 7980.0, "unidad": "gramos (g)"},

        # --- INSUMOS Y EMPAQUES ---
        "Harina de Maíz": {"categoria": "Insumos", "stock": 2.0, "unidad": "paquetes"},
        "Orégano Seco": {"categoria": "Insumos", "stock": 2.0, "unidad": "unidades"},
        "Aliño Preparado": {"categoria": "Insumos", "stock": 1.0, "unidad": "unidades"},
        "Leche Líquida/Polvo": {"categoria": "Insumos", "stock": 4.85, "unidad": "kg/litros"},
        "Aceite Vegetal": {"categoria": "Insumos", "stock": 2.0, "unidad": "litros"},
        "Vinagre": {"categoria": "Insumos", "stock": 1.0, "unidad": "litros"},
        "Bandejas de Aluminio (Llevar)": {"categoria": "Empaques", "stock": 21.0, "unidad": "unidades"},
        "Toallín de Papel": {"categoria": "Empaques", "stock": 1.0, "unidad": "rollos"},
        "Bolsas Plásticas (Paquete)": {"categoria": "Empaques", "stock": 2.0, "unidad": "paquetes"},
        "Pitillos (Paquete)": {"categoria": "Empaques", "stock": 2.0, "unidad": "paquetes"},
        "Bolsas para Hielo (Paquete)": {"categoria": "Empaques", "stock": 3.0, "unidad": "paquetes"},
        "Servilletas (Paquete)": {"categoria": "Empaques", "stock": 1.0, "unidad": "paquetes"},
        "Cubiertos Desechables": {"categoria": "Empaques", "stock": 15.0, "unidad": "unidades"},

        # --- SNACKS Y CHUCHERÍAS ---
        "Galletas Estela": {"categoria": "Chucherías", "stock": 5.0, "unidad": "unidades"},
        "Galletas Rellenas": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades"},
        "Galletas Maxi Coco": {"categoria": "Chucherías", "stock": 16.0, "unidad": "unidades"},
        "Galletas Charmy": {"categoria": "Chucherías", "stock": 10.0, "unidad": "unidades"},
        "Galletas Alternados": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades"},
        "Papas Potata": {"categoria": "Chucherías", "stock": 3.0, "unidad": "unidades"},
        "Galletas Choco Chips": {"categoria": "Chucherías", "stock": 35.0, "unidad": "unidades"},
        "Galletas Escureto": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades"},
        "Galletas Oreo": {"categoria": "Chucherías", "stock": 7.0, "unidad": "unidades"},
        "Galletas TipTop": {"categoria": "Chucherías", "stock": 42.0, "unidad": "unidades"},
        "Palitos": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades"},
        "Flaquito": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades"},
        "Doritos (Grande)": {"categoria": "Chucherías", "stock": 8.0, "unidad": "unidades"},
        "Ruffles (Grande)": {"categoria": "Chucherías", "stock": 6.0, "unidad": "unidades"},
        "Pepito (Grande)": {"categoria": "Chucherías", "stock": 7.0, "unidad": "unidades"},
        "Bilo": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades"},
        "De Todito": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades"},
        "NatuChips": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades"},
        "Lays": {"categoria": "Chucherías", "stock": 6.0, "unidad": "unidades"},
        "Raquety": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades"},
        "Combito": {"categoria": "Chucherías", "stock": 11.0, "unidad": "unidades"},
        "Doritos (Pequeño)": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades"},
        "Cheetos": {"categoria": "Chucherías", "stock": 24.0, "unidad": "unidades"},
        "Cheese Tris": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades"},
        "Kraker Bran": {"categoria": "Chucherías", "stock": 26.0, "unidad": "unidades"},
        "Galletas Hony Bran": {"categoria": "Chucherías", "stock": 27.0, "unidad": "unidades"},
        "Club Social": {"categoria": "Chucherías", "stock": 35.0, "unidad": "unidades"},
        "Galletas Universal": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades"},
        "Chimó": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades"},
        "Caramelos Surtidos": {"categoria": "Chucherías", "stock": 241.0, "unidad": "unidades"},
        "Chupetas": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades"},

        # --- BEBIDAS ---
        "Refresco (1.5 Litros)": {"categoria": "Bebidas", "stock": 108.0, "unidad": "unidades"},
        "Refresco (1 Litro)": {"categoria": "Bebidas", "stock": 99.0, "unidad": "unidades"},
        "Agua Mineral (1.5 Litros)": {"categoria": "Bebidas", "stock": 56.0, "unidad": "unidades"},
        "Agua Mineral (600 ml)": {"categoria": "Bebidas", "stock": 105.0, "unidad": "unidades"},
        "Refresco (2 Litros)": {"categoria": "Bebidas", "stock": 12.0, "unidad": "unidades"},
        "Sangría (Botella Grande)": {"categoria": "Bebidas Alcohólicas", "stock": 12.0, "unidad": "unidades"},
        "Sangría (Lata)": {"categoria": "Bebidas Alcohólicas", "stock": 12.0, "unidad": "unidades"},
        "Malta (Lata)": {"categoria": "Bebidas", "stock": 38.0, "unidad": "unidades"},
        "Jugo Yukery (250 ml)": {"categoria": "Bebidas", "stock": 23.0, "unidad": "unidades"},
        "Jugo Yukery (Grande)": {"categoria": "Bebidas", "stock": 12.0, "unidad": "unidades"},
        "Cerveza": {"categoria": "Bebidas Alcohólicas", "stock": 14.0, "unidad": "unidades"},
        "Gatorade": {"categoria": "Bebidas", "stock": 7.0, "unidad": "unidades"},
        "Té Lipton": {"categoria": "Bebidas", "stock": 6.0, "unidad": "unidades"},
        "Refresco (350 ml)": {"categoria": "Bebidas", "stock": 53.0, "unidad": "unidades"},
        "Agua de Soda": {"categoria": "Bebidas", "stock": 23.0, "unidad": "unidades"},

        # --- CAFÉ Y AZÚCAR ---
        "Café Molido": {"categoria": "Cafetería", "stock": 1.5, "unidad": "kg"},
        "Azúcar Refinada": {"categoria": "Cafetería", "stock": 0.5, "unidad": "kg"},

        # --- VASOS ---
        "Vasos (Medida 37)": {"categoria": "Empaques", "stock": 47.0, "unidad": "unidades"},
        "Vasos (Medida 57)": {"categoria": "Empaques", "stock": 67.0, "unidad": "unidades"},
        "Vasos (Medida 77)": {"categoria": "Empaques", "stock": 70.0, "unidad": "unidades"}
    }

# RECETAS ACTUALIZADAS (Ahora incluye TODAS las opciones de gramos)
if "recetas" not in st.session_state:
    st.session_state.recetas = {
        # Bebidas
        "Jugo de Mora": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Mora": 1.0, "Vasos (Medida 57)": 1.0}},
        "Jugo de Piña": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Piña": 1.0, "Vasos (Medida 57)": 1.0}},
        
        # Parrillas Base
        "Parrilla Mixta (Grande)": {"categoria": "Comida/Parrillas", "precio_usd": 15.00, "ingredientes": {"Carne de Res (Congelada)": 330.0, "Carne de Cerdo (Congelada)": 330.0, "Pollo Entero": 0.25}},
        "Parrilla Mixta (Sencilla)": {"categoria": "Comida/Parrillas", "precio_usd": 8.00, "ingredientes": {"Carne de Res (Congelada)": 110.0, "Carne de Cerdo (Congelada)": 110.0, "Pollo Entero": 0.25}},
        
        # Raciones y Extras (Para que el vendedor las agregue a la lista fácilmente y se descuenten los gramos)
        "Ración Extra de Res (330g)": {"categoria": "Raciones", "precio_usd": 6.00, "ingredientes": {"Carne de Res (Congelada)": 330.0}},
        "Ración Extra de Res (110g)": {"categoria": "Raciones", "precio_usd": 2.50, "ingredientes": {"Carne de Res (Congelada)": 110.0}},
        "Ración Extra de Cerdo (330g)": {"categoria": "Raciones", "precio_usd": 5.00, "ingredientes": {"Carne de Cerdo (Congelada)": 330.0}},
        "Ración Extra de Cerdo (110g)": {"categoria": "Raciones", "precio_usd": 2.00, "ingredientes": {"Carne de Cerdo (Congelada)": 110.0}},
        "Ración Extra de Ovejo (330g)": {"categoria": "Raciones", "precio_usd": 7.00, "ingredientes": {"Carne de Ovejo (Congelada)": 330.0}},
        "Ración Extra de Ovejo (110g)": {"categoria": "Raciones", "precio_usd": 3.00, "ingredientes": {"Carne de Ovejo (Congelada)": 110.0}},
        "Ración Extra de Pollo (1 Cuarto)": {"categoria": "Raciones", "precio_usd": 3.50, "ingredientes": {"Pollo Entero": 0.25}},
    }

if "ventas" not in st.session_state:
    st.session_state.ventas = []
if "totales" not in st.session_state:
    st.session_state.totales = {"Digital": 0.0, "Bs": 0.0, "USD": 0.0}
    
# VARIABLE PARA EL CARRITO DE COMPRAS
if "carrito" not in st.session_state:
    st.session_state.carrito = []

CREDENCIALES = {
    "alejandro": {"pass": "admin2026", "nombre": "Alejandro", "rol": "admin"},
    "jackeline": {"pass": "tiajack123", "nombre": "Jackeline", "rol": "supervisor"},
    "janet": {"pass": "tiajanet123", "nombre": "Janet", "rol": "vendedor"},
    "antonio": {"pass": "antonio123", "nombre": "Antonio", "rol": "vendedor"},
    "andrea": {"pass": "andrea123", "nombre": "Andrea", "rol": "vendedor"}
}

if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = None

if not st.session_state.usuario_actual:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if lottie_login: st_lottie(lottie_login, height=200, key="login_anim")
        else: st.markdown("<h1 style='text-align: center; font-size: 60px;'>🌊</h1>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center;'>Villa Marina</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #b0c4de !important;'>Ingrese credenciales operativas</p>", unsafe_allow_html=True)
        
        user_input = st.text_input("Usuario:")
        pass_input = st.text_input("Contraseña:", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Iniciar Sesión"):
            user_lower = user_input.strip().lower()
            if user_lower in CREDENCIALES and CREDENCIALES[user_lower]["pass"] == pass_input:
                st.session_state.usuario_actual = CREDENCIALES[user_lower]
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

usuario = st.session_state.usuario_actual
st.sidebar.markdown(f"👤 **Conectado como:** {usuario['nombre']} ({usuario['rol'].upper()})")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.title("🛒 Panel Principal - Villa Marina")

opciones_menu = []
if usuario["rol"] == "vendedor": opciones_menu = ["Control de Ventas", "Ver Inventario"]
elif usuario["rol"] == "supervisor": opciones_menu = ["Ver Inventario", "Cierre Diario"]
elif usuario["rol"] == "admin": opciones_menu = ["Ver Inventario", "Gestión de Inventario", "Cierre Diario"]

menu = st.sidebar.selectbox("Navegación", opciones_menu)
st.divider()

# ==========================================
# 1. CONTROL DE VENTAS (SISTEMA DE CARRITO)
# ==========================================
if menu == "Control de Ventas":
    if lottie_ventas: st_lottie(lottie_ventas, height=150, key="ventas_anim")
        
    st.header("🧾 Crear Pedido / Lista de Venta")
    tasa = st.number_input("Tasa del Día (Bs/$):", min_value=0.0, value=36.50, format="%.2f")
    
    st.subheader("1. Agregar productos a la lista")
    tipo_venta = st.radio("Filtro de búsqueda:", ["Plato / Menú (Con Receta y Raciones)", "Insumo Directo / Chucherías / Bebidas"])
    
    if tipo_venta == "Plato / Menú (Con Receta y Raciones)":
        platos_disponibles = list(st.session_state.recetas.keys())
        if platos_disponibles:
            plato_sel = st.selectbox("Seleccione el plato o ración extra:", platos_disponibles)
            cantidad_platos = st.number_input("Cantidad:", min_value=1.0, value=1.0, format="%.1f")
            
            # Sugerir precio automáticamente basado en la receta
            precio_sugerido = st.session_state.recetas[plato_sel]["precio_usd"] * cantidad_platos
            monto_linea = st.number_input("Precio Cobrado ($ o Bs equivalentes):", min_value=0.0, value=precio_sugerido, format="%.2f")
            
            if st.button("➕ Añadir a la Lista"):
                st.session_state.carrito.append({
                    "tipo": "plato", 
                    "item": plato_sel, 
                    "cantidad": cantidad_platos, 
                    "monto": monto_linea
                })
                st.success(f"Agregado: {cantidad_platos}x {plato_sel}")
                st.rerun()
    else:
        item_sel = st.selectbox("Seleccione el producto:", list(st.session_state.inventario.keys()))
        cant_suelta = st.number_input("Cantidad:", min_value=1.0, value=1.0, format="%.1f")
        monto_linea = st.number_input("Precio Cobrado ($ o Bs equivalentes):", min_value=0.0, value=0.0, format="%.2f")
        
        if st.button("➕ Añadir a la Lista"):
            st.session_state.carrito.append({
                "tipo": "insumo", 
                "item": item_sel, 
                "cantidad": cant_suelta, 
                "monto": monto_linea
            })
            st.success(f"Agregado: {cant_suelta}x {item_sel}")
            st.rerun()

    st.divider()
    st.subheader("2. Resumen de la Mesa y Pago")
    
    if st.session_state.carrito:
        df_carrito = pd.DataFrame([{
            "Producto": item["item"], 
            "Cant.": item["cantidad"], 
            "Subtotal ($ o Bs)": item["monto"]
        } for item in st.session_state.carrito])
        
        st.dataframe(df_carrito, use_container_width=True)
        
        total_monto = sum(item["monto"] for item in st.session_state.carrito)
        st.markdown(f"### 💰 Total a Registrar: {total_monto:.2f}")
        
        if st.button("🗑️ Vaciar Lista"):
            st.session_state.carrito = []
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        metodo = st.selectbox("Método de pago final:", [
            "Digital (Pago Móvil / Punto)", 
            "Físico (Bolívares)", 
            "Físico (Dólares)",
            "🎁 Cortesía / Personal (No genera ingreso)"
        ])
        
        if st.button("✅ Facturar y Descontar Inventario", type="primary"):
            requerimientos = {}
            for linea in st.session_state.carrito:
                if linea["tipo"] == "plato":
                    receta = st.session_state.recetas[linea["item"]]["ingredientes"]
                    for ing, cant_receta in receta.items():
                        requerimientos[ing] = requerimientos.get(ing, 0) + (cant_receta * linea["cantidad"])
                else:
                    requerimientos[linea["item"]] = requerimientos.get(linea["item"], 0) + linea["cantidad"]
            
            faltantes = []
            for ing, cant_req in requerimientos.items():
                if st.session_state.inventario[ing]["stock"] < cant_req:
                    faltantes.append(f"{ing} (Faltan {cant_req - st.session_state.inventario[ing]['stock']} {st.session_state.inventario[ing]['unidad']})")
                    
            if faltantes:
                st.error("❌ Stock insuficiente. La venta no se procesó. Faltan los siguientes productos:\n\n" + "\n".join(faltantes))
            else:
                for ing, cant_req in requerimientos.items():
                    st.session_state.inventario[ing]["stock"] -= cant_req
                
                if "Cortesía" not in metodo:
                    if "Digital" in metodo: st.session_state.totales["Digital"] += total_monto
                    elif "Bolívares" in metodo: st.session_state.totales["Bs"] += total_monto
                    else: st.session_state.totales["USD"] += total_monto
                
                resumen_venta = ", ".join([f"{i['cantidad']}x {i['item']}" for i in st.session_state.carrito])
                st.session_state.ventas.append({
                    "hora": datetime.now().strftime('%I:%M %p'), 
                    "vendedor": usuario["nombre"], 
                    "pedido": resumen_venta, 
                    "monto_total": total_monto if "Cortesía" not in metodo else 0.0, 
                    "metodo": metodo
                })
                
                st.session_state.carrito = []
                st.success("✅ ¡Venta procesada con éxito! El inventario se ha actualizado en gramos y unidades.")
                st.rerun()
                
    else:
        st.info("La lista está vacía. Agrega productos arriba para comenzar una venta.")

# ==========================================
# 2. VER INVENTARIO
# ==========================================
elif menu == "Ver Inventario":
    if lottie_inventario: st_lottie(lottie_inventario, height=150, key="inv_anim")
        
    st.header("📦 Inventario Actual")
    if st.session_state.inventario:
        df_inv = pd.DataFrame([{"Categoría": v["categoria"], "Producto": k, "Stock": v["stock"], "Unidad": v["unidad"]} for k, v in st.session_state.inventario.items()])
        st.dataframe(df_inv, use_container_width=True)

# ==========================================
# 3. GESTIÓN DE INVENTARIO (Admin)
# ==========================================
elif menu == "Gestión de Inventario":
    if lottie_inventario: st_lottie(lottie_inventario, height=120, key="gest_inv_anim")
        
    st.header("⚙️ Gestión de Almacén")
    prod_existente = st.selectbox("Insumo a modificar:", list(st.session_state.inventario.keys()))
    cant_agrega = st.number_input("Cantidad a sumar/restar (usa - para restar):", format="%.2f")
    if st.button("Actualizar Stock General"):
        st.session_state.inventario[prod_existente]["stock"] += cant_agrega
        st.success(f"✅ Stock de {prod_existente} actualizado con éxito.")

# ==========================================
# 4. CIERRE DIARIO
# ==========================================
elif menu == "Cierre Diario":
    if lottie_cierre: st_lottie(lottie_cierre, height=150, key="cierre_anim")
        
    st.header("📊 Cierre de Caja")
    tasa_cierre = st.number_input("Tasa aplicada (Bs/$):", min_value=0.0, value=36.50, format="%.2f")
    if st.button("Calcular Cierre"):
        tot_dig, tot_bs, tot_usd = st.session_state.totales["Digital"], st.session_state.totales["Bs"], st.session_state.totales["USD"]
        gran_total = tot_usd + ((tot_dig + tot_bs) / tasa_cierre if tasa_cierre > 0 else 0)
        
        st.markdown(f"### 💵 Total Equivalente Real: {gran_total:.2f} $")
        st.caption("Nota: Las ventas marcadas como 'Cortesía' descuentan inventario pero no se suman a esta caja.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Digital (Bs)", f"{tot_dig:.2f}")
        col2.metric("Efectivo (Bs)", f"{tot_bs:.2f}")
        col3.metric("Efectivo ($)", f"{tot_usd:.2f}")
        
        st.divider()
        st.subheader("📝 Historial Detallado de Ventas")
        if st.session_state.ventas:
            st.dataframe(pd.DataFrame(st.session_state.ventas), use_container_width=True)
        else:
            st.info("No hay ventas registradas en este turno.")