import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import json
from streamlit_lottie import st_lottie
from PIL import Image
from pyzbar.pyzbar import decode

# Configuración de página
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

# --- OBSERVACIÓN 1: CSS DINÁMICO (CLARO/OSCURO) ---
# Se usan variables nativas de Streamlit para que el texto y fondo se adapten automáticamente
if bg_image_base64:
    bg_css = f"""
    background-image: linear-gradient(var(--background-color), var(--background-color)), url('data:image/jpeg;base64,{bg_image_base64}');
    background-blend-mode: overlay;
    background-size: cover; 
    background-position: center; 
    background-attachment: fixed;
    """
else:
    bg_css = "background-color: var(--background-color);"

st.markdown(f"""
<style>
    .stApp {{ {bg_css} }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} 
    iframe {{ background-color: transparent !important; border: none !important; }}
    
    /* Contenedores con Glassmorphism que se adaptan al tema */
    .block-container {{
        background: var(--secondary-background-color) !important;
        opacity: 0.95;
        border-radius: 20px;
        padding: 3rem 2rem !important;
        margin-top: 2rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }}
    
    /* Textos adaptables */
    h1, h2, h3, p, label, .stMarkdown {{
        color: var(--text-color) !important; 
    }}
    
    /* Botones y campos de texto */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{ 
        background-color: var(--background-color) !important; 
        color: var(--text-color) !important; 
        border-radius: 8px !important; 
    }}
    .stButton > button {{ 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        width: 100%; 
    }}
</style>
""", unsafe_allow_html=True)


# --- OBSERVACIÓN 3: PRECIOS EN CADA PRODUCTO ---
if "inventario" not in st.session_state:
    st.session_state.inventario = {
        # --- CARNES (Materia Prima General) ---
        "Pollo Entero": {"categoria": "Carnes", "stock": 59.0, "unidad": "unidades", "precio_usd": 6.50, "codigo_barras": ""},
        "Nuggets de Pollo (Bandeja)": {"categoria": "Carnes", "stock": 3.0, "unidad": "bandejas", "precio_usd": 4.00, "codigo_barras": ""},
        "Chorizo Artesanal": {"categoria": "Carnes", "stock": 44.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Carne de Res (Congelada)": {"categoria": "Carnes", "stock": 7725.0, "unidad": "gramos (g)", "precio_usd": 0.008, "codigo_barras": ""}, # $8 el kg
        "Carne de Cerdo (Congelada)": {"categoria": "Carnes", "stock": 5530.0, "unidad": "gramos (g)", "precio_usd": 0.007, "codigo_barras": ""}, # $7 el kg
        "Carne de Ovejo (Congelada)": {"categoria": "Carnes", "stock": 2500.0, "unidad": "gramos (g)", "precio_usd": 0.009, "codigo_barras": ""}, # $9 el kg
        "Papas Fritas (Bolsa Completa)": {"categoria": "Carnes", "stock": 2.0, "unidad": "bolsas", "precio_usd": 3.50, "codigo_barras": ""},
        "Papas Fritas (Porción)": {"categoria": "Carnes", "stock": 6.0, "unidad": "porciones", "precio_usd": 1.50, "codigo_barras": ""},

        # --- PULPAS DE FRUTAS ---
        "Pulpa de Piña": {"categoria": "Pulpas", "stock": 6.0, "unidad": "porciones", "precio_usd": 1.00, "codigo_barras": ""},
        "Pulpa de Mora": {"categoria": "Pulpas", "stock": 12.0, "unidad": "porciones", "precio_usd": 1.20, "codigo_barras": ""},
        "Pulpa de Guanábana": {"categoria": "Pulpas", "stock": 17.0, "unidad": "porciones", "precio_usd": 1.50, "codigo_barras": ""},
        "Pulpa de Durazno": {"categoria": "Pulpas", "stock": 13.0, "unidad": "porciones", "precio_usd": 1.30, "codigo_barras": ""},
        "Pulpa de Parchita": {"categoria": "Pulpas", "stock": 9.0, "unidad": "porciones", "precio_usd": 1.20, "codigo_barras": ""},
        "Pulpa de Fresa": {"categoria": "Pulpas", "stock": 12.0, "unidad": "porciones", "precio_usd": 1.50, "codigo_barras": ""},

        # --- GUARNICIONES ---
        "Yuca Fresca": {"categoria": "Guarniciones", "stock": 7980.0, "unidad": "gramos (g)", "precio_usd": 0.0015, "codigo_barras": ""}, # $1.5 el kg

        # --- INSUMOS Y EMPAQUES ---
        "Harina de Maíz": {"categoria": "Insumos", "stock": 2.0, "unidad": "paquetes", "precio_usd": 1.20, "codigo_barras": ""},
        "Orégano Seco": {"categoria": "Insumos", "stock": 2.0, "unidad": "unidades", "precio_usd": 0.50, "codigo_barras": ""},
        "Aliño Preparado": {"categoria": "Insumos", "stock": 1.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Leche Líquida/Polvo": {"categoria": "Insumos", "stock": 4.85, "unidad": "kg/litros", "precio_usd": 1.80, "codigo_barras": ""},
        "Aceite Vegetal": {"categoria": "Insumos", "stock": 2.0, "unidad": "litros", "precio_usd": 3.00, "codigo_barras": ""},
        "Vinagre": {"categoria": "Insumos", "stock": 1.0, "unidad": "litros", "precio_usd": 1.50, "codigo_barras": ""},
        "Bandejas de Aluminio (Llevar)": {"categoria": "Empaques", "stock": 21.0, "unidad": "unidades", "precio_usd": 0.30, "codigo_barras": ""},
        "Toallín de Papel": {"categoria": "Empaques", "stock": 1.0, "unidad": "rollos", "precio_usd": 1.00, "codigo_barras": ""},
        "Bolsas Plásticas (Paquete)": {"categoria": "Empaques", "stock": 2.0, "unidad": "paquetes", "precio_usd": 2.00, "codigo_barras": ""},
        "Pitillos (Paquete)": {"categoria": "Empaques", "stock": 2.0, "unidad": "paquetes", "precio_usd": 1.50, "codigo_barras": ""},
        "Bolsas para Hielo (Paquete)": {"categoria": "Empaques", "stock": 3.0, "unidad": "paquetes", "precio_usd": 1.00, "codigo_barras": ""},
        "Servilletas (Paquete)": {"categoria": "Empaques", "stock": 1.0, "unidad": "paquetes", "precio_usd": 1.20, "codigo_barras": ""},
        "Cubiertos Desechables": {"categoria": "Empaques", "stock": 15.0, "unidad": "unidades", "precio_usd": 0.10, "codigo_barras": ""},

        # --- SNACKS Y CHUCHERÍAS ---
        "Galletas Estela": {"categoria": "Chucherías", "stock": 5.0, "unidad": "unidades", "precio_usd": 0.80, "codigo_barras": ""},
        "Galletas Rellenas": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Galletas Maxi Coco": {"categoria": "Chucherías", "stock": 16.0, "unidad": "unidades", "precio_usd": 0.70, "codigo_barras": ""},
        "Galletas Charmy": {"categoria": "Chucherías", "stock": 10.0, "unidad": "unidades", "precio_usd": 0.50, "codigo_barras": ""},
        "Galletas Alternados": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades", "precio_usd": 0.90, "codigo_barras": ""},
        "Papas Potata": {"categoria": "Chucherías", "stock": 3.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
        "Galletas Choco Chips": {"categoria": "Chucherías", "stock": 35.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Galletas Escureto": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Galletas Oreo": {"categoria": "Chucherías", "stock": 7.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": "7591000333444"},
        "Galletas TipTop": {"categoria": "Chucherías", "stock": 42.0, "unidad": "unidades", "precio_usd": 0.80, "codigo_barras": ""},
        "Palitos": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Flaquito": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades", "precio_usd": 0.60, "codigo_barras": ""},
        "Doritos (Grande)": {"categoria": "Chucherías", "stock": 8.0, "unidad": "unidades", "precio_usd": 3.00, "codigo_barras": "7591000555666"},
        "Ruffles (Grande)": {"categoria": "Chucherías", "stock": 6.0, "unidad": "unidades", "precio_usd": 3.00, "codigo_barras": ""},
        "Pepito (Grande)": {"categoria": "Chucherías", "stock": 7.0, "unidad": "unidades", "precio_usd": 2.50, "codigo_barras": ""},
        "Bilo": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades", "precio_usd": 0.50, "codigo_barras": ""},
        "De Todito": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades", "precio_usd": 2.50, "codigo_barras": ""},
        "NatuChips": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades", "precio_usd": 2.00, "codigo_barras": ""},
        "Lays": {"categoria": "Chucherías", "stock": 6.0, "unidad": "unidades", "precio_usd": 2.50, "codigo_barras": ""},
        "Raquety": {"categoria": "Chucherías", "stock": 12.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Combito": {"categoria": "Chucherías", "stock": 11.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Doritos (Pequeño)": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Cheetos": {"categoria": "Chucherías", "stock": 24.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Cheese Tris": {"categoria": "Chucherías", "stock": 9.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Kraker Bran": {"categoria": "Chucherías", "stock": 26.0, "unidad": "unidades", "precio_usd": 0.80, "codigo_barras": ""},
        "Galletas Hony Bran": {"categoria": "Chucherías", "stock": 27.0, "unidad": "unidades", "precio_usd": 0.90, "codigo_barras": ""},
        "Club Social": {"categoria": "Chucherías", "stock": 35.0, "unidad": "unidades", "precio_usd": 0.70, "codigo_barras": ""},
        "Galletas Universal": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades", "precio_usd": 0.50, "codigo_barras": ""},
        "Chimó": {"categoria": "Chucherías", "stock": 4.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
        "Caramelos Surtidos": {"categoria": "Chucherías", "stock": 241.0, "unidad": "unidades", "precio_usd": 0.10, "codigo_barras": ""},
        "Chupetas": {"categoria": "Chucherías", "stock": 2.0, "unidad": "unidades", "precio_usd": 0.30, "codigo_barras": ""},

        # --- BEBIDAS ---
        "Refresco (1.5 Litros)": {"categoria": "Bebidas", "stock": 108.0, "unidad": "unidades", "precio_usd": 2.50, "codigo_barras": "7591000111222"},
        "Refresco (1 Litro)": {"categoria": "Bebidas", "stock": 99.0, "unidad": "unidades", "precio_usd": 2.00, "codigo_barras": ""},
        "Agua Mineral (1.5 Litros)": {"categoria": "Bebidas", "stock": 56.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
        "Agua Mineral (600 ml)": {"categoria": "Bebidas", "stock": 105.0, "unidad": "unidades", "precio_usd": 0.80, "codigo_barras": ""},
        "Refresco (2 Litros)": {"categoria": "Bebidas", "stock": 12.0, "unidad": "unidades", "precio_usd": 3.00, "codigo_barras": ""},
        "Sangría (Botella Grande)": {"categoria": "Bebidas Alcohólicas", "stock": 12.0, "unidad": "unidades", "precio_usd": 6.00, "codigo_barras": ""},
        "Sangría (Lata)": {"categoria": "Bebidas Alcohólicas", "stock": 12.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
        "Malta (Lata)": {"categoria": "Bebidas", "stock": 38.0, "unidad": "unidades", "precio_usd": 1.20, "codigo_barras": ""},
        "Jugo Yukery (250 ml)": {"categoria": "Bebidas", "stock": 23.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Jugo Yukery (Grande)": {"categoria": "Bebidas", "stock": 12.0, "unidad": "unidades", "precio_usd": 2.50, "codigo_barras": ""},
        "Cerveza": {"categoria": "Bebidas Alcohólicas", "stock": 14.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": "7591000777888"},
        "Gatorade": {"categoria": "Bebidas", "stock": 7.0, "unidad": "unidades", "precio_usd": 1.80, "codigo_barras": ""},
        "Té Lipton": {"categoria": "Bebidas", "stock": 6.0, "unidad": "unidades", "precio_usd": 1.50, "codigo_barras": ""},
        "Refresco (350 ml)": {"categoria": "Bebidas", "stock": 53.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},
        "Agua de Soda": {"categoria": "Bebidas", "stock": 23.0, "unidad": "unidades", "precio_usd": 1.00, "codigo_barras": ""},

        # --- CAFÉ Y AZÚCAR ---
        "Café Molido": {"categoria": "Cafetería", "stock": 1.5, "unidad": "kg", "precio_usd": 8.00, "codigo_barras": ""},
        "Azúcar Refinada": {"categoria": "Cafetería", "stock": 0.5, "unidad": "kg", "precio_usd": 1.50, "codigo_barras": ""},

        # --- VASOS ---
        "Vasos (Medida 37)": {"categoria": "Empaques", "stock": 47.0, "unidad": "unidades", "precio_usd": 0.10, "codigo_barras": ""},
        "Vasos (Medida 57)": {"categoria": "Empaques", "stock": 67.0, "unidad": "unidades", "precio_usd": 0.15, "codigo_barras": ""},
        "Vasos (Medida 77)": {"categoria": "Empaques", "stock": 70.0, "unidad": "unidades", "precio_usd": 0.20, "codigo_barras": ""}
    }

if "recetas" not in st.session_state:
    st.session_state.recetas = {
        "Jugo de Mora": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Mora": 1.0, "Vasos (Medida 57)": 1.0}},
        "Jugo de Piña": {"categoria": "Bebidas", "precio_usd": 2.50, "ingredientes": {"Pulpa de Piña": 1.0, "Vasos (Medida 57)": 1.0}},
        "Parrilla Mixta (Grande)": {"categoria": "Comida/Parrillas", "precio_usd": 15.00, "ingredientes": {"Carne de Res (Congelada)": 330.0, "Carne de Cerdo (Congelada)": 330.0, "Pollo Entero": 0.25}},
        "Parrilla Mixta (Sencilla)": {"categoria": "Comida/Parrillas", "precio_usd": 8.00, "ingredientes": {"Carne de Res (Congelada)": 110.0, "Carne de Cerdo (Congelada)": 110.0, "Pollo Entero": 0.25}},
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
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "estadisticas_items" not in st.session_state:
    st.session_state.estadisticas_items = {}

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
        st.markdown("<p style='text-align: center;'>Ingrese credenciales operativas</p>", unsafe_allow_html=True)
        
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
elif usuario["rol"] == "admin": opciones_menu = ["Ver Inventario", "Gestión de Inventario", "Cierre y Estadísticas"]

menu = st.sidebar.selectbox("Navegación", opciones_menu)
st.divider()

# ==========================================
# 1. CONTROL DE VENTAS (SISTEMA DE CARRITO)
# ==========================================
if menu == "Control de Ventas":
    if lottie_ventas: st_lottie(lottie_ventas, height=150, key="ventas_anim")
        
    st.header("🧾 Crear Pedido / Lista de Venta")
    tasa = st.number_input("Tasa del Día (Bs/$):", min_value=0.0, value=36.50, format="%.2f")
    
    # --- OBSERVACIÓN 2: ESCÁNER DE CÓDIGO DE BARRAS ---
    st.subheader("📷 Escanear con la cámara")
    foto_codigo = st.camera_input("Enfoca el código de barras de la chuchería/bebida")

    if foto_codigo is not None:
        imagen = Image.open(foto_codigo)
        codigos_detectados = decode(imagen)
        
        if codigos_detectados:
            for codigo in codigos_detectados:
                codigo_leido = codigo.data.decode('utf-8')
                
                encontrado = False
                for nombre_prod, datos in st.session_state.inventario.items():
                    if datos.get("codigo_barras") == codigo_leido:
                        precio = datos.get("precio_usd", 0.0)
                        st.session_state.carrito.append({"tipo": "insumo", "item": nombre_prod, "cantidad": 1.0, "monto": precio})
                        st.success(f"✅ ¡Escaneado con éxito! Agregado: 1x {nombre_prod} (${precio})")
                        encontrado = True
                        break
                
                if not encontrado:
                    st.warning(f"❌ Se leyó el código ({codigo_leido}), pero no está registrado en tu inventario.")
        else:
            st.error("No se detectó ningún código. Intenta acercar la cámara o mejorar la iluminación.")

    st.markdown("---")
    st.subheader("⌨️ O ingresarlo manualmente")
    with st.form(key="form_codigo_manual", clear_on_submit=True):
        codigo_manual = st.text_input("Escribe el código o usa una pistola lectora USB:")
        if st.form_submit_button("Agregar por Código Manual") and codigo_manual:
            encontrado = False
            for nombre_prod, datos in st.session_state.inventario.items():
                if datos.get("codigo_barras") == codigo_manual.strip():
                    precio = datos.get("precio_usd", 0.0)
                    st.session_state.carrito.append({"tipo": "insumo", "item": nombre_prod, "cantidad": 1.0, "monto": precio})
                    st.success(f"✅ Agregado: 1x {nombre_prod} (${precio})")
                    encontrado = True
                    break
            if not encontrado:
                st.error("❌ Código no encontrado.")

    st.subheader("🔍 Búsqueda en el Menú")
    tipo_venta = st.radio("Filtro de búsqueda:", ["Plato / Menú (Con Receta y Raciones)", "Insumo Directo / Chucherías / Bebidas"])
    
    if tipo_venta == "Plato / Menú (Con Receta y Raciones)":
        platos_disponibles = list(st.session_state.recetas.keys())
        if platos_disponibles:
            plato_sel = st.selectbox("Seleccione el plato o ración extra:", platos_disponibles)
            cantidad_platos = st.number_input("Cantidad:", min_value=1.0, value=1.0, format="%.1f")
            precio_sugerido = st.session_state.recetas[plato_sel]["precio_usd"] * cantidad_platos
            monto_linea = st.number_input("Precio Cobrado ($ o Bs equivalentes):", min_value=0.0, value=precio_sugerido, format="%.2f")
            
            if st.button("➕ Añadir a la Lista"):
                st.session_state.carrito.append({"tipo": "plato", "item": plato_sel, "cantidad": cantidad_platos, "monto": monto_linea})
                st.success(f"Agregado: {cantidad_platos}x {plato_sel}")
                st.rerun()
    else:
        item_sel = st.selectbox("Seleccione el producto:", list(st.session_state.inventario.keys()))
        cant_suelta = st.number_input("Cantidad:", min_value=1.0, value=1.0, format="%.1f")
        precio_unitario = st.session_state.inventario[item_sel].get("precio_usd", 0.0)
        precio_sugerido = precio_unitario * cant_suelta
        monto_linea = st.number_input("Precio Cobrado ($ o Bs equivalentes):", min_value=0.0, value=precio_sugerido, format="%.2f")
        
        if st.button("➕ Añadir a la Lista"):
            st.session_state.carrito.append({"tipo": "insumo", "item": item_sel, "cantidad": cant_suelta, "monto": monto_linea})
            st.success(f"Agregado: {cant_suelta}x {item_sel}")
            st.rerun()

    st.divider()
    st.subheader("2. Resumen de la Mesa y Pago")
    
    if st.session_state.carrito:
        df_carrito = pd.DataFrame([{"Producto": item["item"], "Cant.": item["cantidad"], "Subtotal ($ o Bs)": item["monto"]} for item in st.session_state.carrito])
        st.dataframe(df_carrito, use_container_width=True)
        
        total_monto = sum(item["monto"] for item in st.session_state.carrito)
        st.markdown(f"### 💰 Total a Registrar: {total_monto:.2f}")
        
        if st.button("🗑️ Vaciar Lista"):
            st.session_state.carrito = []
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        metodo = st.selectbox("Método de pago final:", ["Digital (Pago Móvil / Punto)", "Físico (Bolívares)", "Físico (Dólares)", "🎁 Cortesía / Personal (No genera ingreso)"])
        
        if st.button("✅ Facturar y Descontar Inventario", type="primary"):
            requerimientos = {}
            for linea in st.session_state.carrito:
                if linea["tipo"] == "plato":
                    receta = st.session_state.recetas[linea["item"]]["ingredientes"]
                    for ing, cant_receta in receta.items():
                        requerimientos[ing] = requerimientos.get(ing, 0) + (cant_receta * linea["cantidad"])
                else:
                    requerimientos[linea["item"]] = requerimientos.get(linea["item"], 0) + linea["cantidad"]
            
            # --- OBSERVACIÓN 4: GUARDAR DATOS ESTADÍSTICOS ---
            for linea in st.session_state.carrito:
                nombre_item = linea["item"]
                st.session_state.estadisticas_items[nombre_item] = st.session_state.estadisticas_items.get(nombre_item, 0) + linea["cantidad"]

            faltantes = []
            for ing, cant_req in requerimientos.items():
                if st.session_state.inventario[ing]["stock"] < cant_req:
                    faltantes.append(f"{ing} (Faltan {cant_req - st.session_state.inventario[ing]['stock']} {st.session_state.inventario[ing]['unidad']})")
                    
            if faltantes:
                st.error("❌ Stock insuficiente. La venta no se procesó. Faltan:\n\n" + "\n".join(faltantes))
            else:
                for ing, cant_req in requerimientos.items():
                    st.session_state.inventario[ing]["stock"] -= cant_req
                
                if "Cortesía" not in metodo:
                    if "Digital" in metodo: st.session_state.totales["Digital"] += total_monto
                    elif "Bolívares" in metodo: st.session_state.totales["Bs"] += total_monto
                    else: st.session_state.totales["USD"] += total_monto
                
                resumen_venta = ", ".join([f"{i['cantidad']}x {i['item']}" for i in st.session_state.carrito])
                st.session_state.ventas.append({"hora": datetime.now().strftime('%I:%M %p'), "vendedor": usuario["nombre"], "pedido": resumen_venta, "monto_total": total_monto if "Cortesía" not in metodo else 0.0, "metodo": metodo})
                
                st.session_state.carrito = []
                st.success("✅ ¡Venta procesada con éxito! El inventario se ha actualizado.")
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
        # Se muestra la columna extra "Precio ($)" para visualizar el ajuste que hicimos
        df_inv = pd.DataFrame([{"Categoría": v["categoria"], "Producto": k, "Stock": v["stock"], "Unidad": v["unidad"], "Precio ($)": v["precio_usd"]} for k, v in st.session_state.inventario.items()])
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
# 4. CIERRE DIARIO Y ESTADÍSTICAS
# ==========================================
elif menu == "Cierre y Estadísticas" or menu == "Cierre Diario":
    if lottie_cierre: st_lottie(lottie_cierre, height=150, key="cierre_anim")
        
    st.header("📊 Cierre de Caja y Estadísticas")
    tasa_cierre = st.number_input("Tasa aplicada (Bs/$):", min_value=0.0, value=36.50, format="%.2f")

    # --- OBSERVACIÓN 4: PESTAÑA DEDICADA A ESTADÍSTICAS MENSUALES/TURNO ---
    tab1, tab2 = st.tabs(["Cierre de Dinero", "📈 Estadísticas de Ventas (Top)"])

    with tab1:
        if st.button("Calcular Cierre"):
            tot_dig, tot_bs, tot_usd = st.session_state.totales["Digital"], st.session_state.totales["Bs"], st.session_state.totales["USD"]
            gran_total = tot_usd + ((tot_dig + tot_bs) / tasa_cierre if tasa_cierre > 0 else 0)
            
            st.markdown(f"### 💵 Total Equivalente Real: {gran_total:.2f} $")
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

    with tab2:
        st.subheader("Productos con Mayor Venta (Cierre Mensual / Turno)")
        st.markdown("Visualiza qué productos han rotado más para tomar decisiones de re-abastecimiento.")
        
        if st.session_state.estadisticas_items:
            # Gráfica interactiva de los artículos más vendidos
            df_stats = pd.DataFrame(list(st.session_state.estadisticas_items.items()), columns=["Producto", "Cantidad Vendida"])
            df_stats = df_stats.sort_values("Cantidad Vendida", ascending=False).set_index("Producto")
            
            st.bar_chart(df_stats)
            st.dataframe(df_stats, use_container_width=True)
        else:
            st.info("Aún no hay ventas registradas para generar el gráfico de estadísticas.")
