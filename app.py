import streamlit as st
import pandas as pd
import base64
import os
import json
import hashlib
from datetime import datetime, date
from streamlit_lottie import st_lottie
from PIL import Image
from pyzbar.pyzbar import decode
import database as db

st.set_page_config(page_title="Control de Ventas - Villa Marina", page_icon="🛒", layout="centered", initial_sidebar_state="expanded")
db.init_db()

def load_f(p, j=False):
    if os.path.exists(p):
        if j:
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
        else:
            with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

bg = load_f("assets/fondo_marino.jpg")
l_log = load_f("assets/animacion_login.json", True)
l_ven = load_f("assets/animacion_ventas.json", True)
l_inv = load_f("assets/animacion_inventario.json", True)
l_cie = load_f("assets/animacion_cierre.json", True)

bg_c = (
    f"background-image: linear-gradient(var(--background-color), var(--background-color)), url('data:image/jpeg;base64,{bg}'); "
    "background-blend-mode: overlay; background-size: cover; background-position: center; background-attachment: fixed;"
    if bg else "background-color: var(--background-color);"
)

st.markdown(f"""
<style>
    .stApp {{ {bg_c} }}
    #MainMenu, footer {{visibility: hidden;}}
    .block-container {{ background: var(--secondary-background-color) !important; opacity: 0.95; border-radius: 20px; padding: 2.5rem 2rem !important; margin-top: 1.5rem !important; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
    h1, h2, h3, p, label, .stMarkdown {{ color: var(--text-color) !important; }}
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{ background-color: var(--background-color) !important; color: var(--text-color) !important; border-radius: 8px !important; }}
    .stButton > button {{ border-radius: 8px !important; font-weight: 600 !important; width: 100%; }}
</style>
""", unsafe_allow_html=True)

PRECIO_MAX_LINEA = 500.0
CANTIDAD_MAX_LINEA = 500.0
CATEGORIA_ICONOS = {"Carnes": "🥩", "Aves": "🐔", "Guarniciones": "🍟", "Insumos": "🧂", "Comida": "🍲", "Pulpas": "🧃", "Empaques": "📦", "Chucherías": "🍪", "Bebidas": "🥤"}

def mostrar_inventario_por_categoria(inv: dict, expandir_todo: bool = False):
    categorias = sorted({v["categoria"] for v in inv.values()})
    for cat in categorias:
        icono = CATEGORIA_ICONOS.get(cat, "📁")
        filas = [{"Producto": k, "Stock": v["stock"], "Unidad": v["unidad"], "Precio ($)": v["precio_usd"]} for k, v in inv.items() if v["categoria"] == cat]
        with st.expander(f"{icono} {cat} ({len(filas)})", expanded=expandir_todo):
            st.dataframe(pd.DataFrame(filas), use_container_width=True)

if "carrito" not in st.session_state: st.session_state.carrito = []
if "ultimo_codigo_hash" not in st.session_state: st.session_state.ultimo_codigo_hash = None
if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = None

# ================= LOGIN =================
if not st.session_state.usuario_actual:
    if not db.hay_usuarios():
        st.warning("⚠️ Aún no hay usuarios configurados. Ejecuta `python setup_usuarios.py` para crear un rol `admin`.")
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if l_log: st_lottie(l_log, height=200)
        st.markdown("<h2 style='text-align: center;'>Villa Marina</h2><p style='text-align: center;'>Ingrese credenciales</p>", unsafe_allow_html=True)
        u = st.text_input("Usuario:")
        p = st.text_input("Contraseña:", type="password")
        if st.button("Iniciar Sesión"):
            usuario_verificado = db.verificar_credenciales(u, p)
            if usuario_verificado:
                st.session_state.usuario_actual = usuario_verificado
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")
    st.stop()

usuario = st.session_state.usuario_actual
st.sidebar.markdown(f"👤 **Conectado:** {usuario['nombre']} ({usuario['rol'].upper()})")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

st.title("🛒 Panel Principal - Villa Marina")

opcs = ["Control de Ventas", "Ver Inventario"] if usuario["rol"] == "vendedor" else (
    ["Ver Inventario", "Cierre Diario"] if usuario["rol"] == "supervisor" else
    ["Ver Inventario", "Gestión de Inventario", "Cierre y Estadísticas"]
)
menu = st.sidebar.selectbox("Navegación", opcs)
st.divider()

inventario = db.obtener_inventario()
recetas_db = db.obtener_recetas()

# ================= CONTROL DE VENTAS =================
if menu == "Control de Ventas":
    if l_ven: st_lottie(l_ven, height=120)
    st.header("🧾 Crear Pedido / Grill Menu")
    tasa = st.number_input("Tasa del Día (Bs/$):", min_value=0.0, value=36.50, format="%.2f")

    foto = st.camera_input("Escanear Código de Barras")
    if foto:
        hash_foto = hashlib.md5(foto.getvalue()).hexdigest()
        if hash_foto != st.session_state.ultimo_codigo_hash:
            st.session_state.ultimo_codigo_hash = hash_foto
            res = decode(Image.open(foto))
            if res:
                c_leido = res[0].data.decode("utf-8")
                encontrado = False
                for k, v in inventario.items():
                    if v.get("codigo_barras") == c_leido:
                        st.session_state.carrito.append({"tipo": "insumo", "item": k, "cantidad": 1.0, "monto": v["precio_usd"]})
                        st.success(f"✅ Agregado: 1x {k} (${v['precio_usd']})")
                        encontrado = True
                        break
                if not encontrado:
                    st.warning(f"❌ Código {c_leido} no registrado.")

    tipo_v = st.selectbox("Sección:", ["Parrilla Personal / Familiar (Fijas)", "Parrilla Mixta Personalizada", "Servicios Adicionales", "Bebidas y Chucherías"])

    if tipo_v == "Parrilla Personal / Familiar (Fijas)":
        plato = st.selectbox("Plato:", [k for k in recetas_db if "Mixta" not in k])
        cant = st.number_input("Cantidad:", min_value=1.0, max_value=CANTIDAD_MAX_LINEA, value=1.0)
        monto = st.number_input("Precio ($):", min_value=0.0, max_value=PRECIO_MAX_LINEA, value=min(recetas_db[plato]["precio_usd"] * cant, PRECIO_MAX_LINEA))
        if st.button("➕ Añadir"):
            st.session_state.carrito.append({"tipo": "plato", "item": plato, "cantidad": cant, "monto": monto})
            st.success(f"Añadido: {cant}x {plato}")
            st.rerun()

    elif tipo_v == "Parrilla Mixta Personalizada":
        t_m = st.selectbox("Tipo:", ["2 Proteínas - 11$", "3 Proteínas - 12$", "4 Proteínas - 13$", "5 Proteínas - 14$"])
        cant_m = st.number_input("Cantidad:", min_value=1.0, max_value=CANTIDAD_MAX_LINEA, value=1.0)
        n_p = int(t_m[0])
        p_val = 11.0 if n_p == 2 else (12.0 if n_p == 3 else (13.0 if n_p == 4 else 14.0))

        st.caption("🐔 El pollo siempre va incluido como base de la mixta.")
        otras_prots = ["Carne de Res (Congelada)", "Carne de Cerdo (Congelada)", "Carne de Ovejo (Congelada)", "Chorizo Artesanal"]
        seleccion_extra = st.multiselect(f"Elige {n_p - 1} proteína(s) adicional(es):", otras_prots)
        prots = ["Pollo (Cuartos)"] + seleccion_extra

        monto_m = st.number_input("Precio ($):", min_value=0.0, max_value=PRECIO_MAX_LINEA, value=min(p_val * cant_m, PRECIO_MAX_LINEA))
        faltan = (n_p - 1) - len(seleccion_extra)
        if faltan != 0:
            st.info(f"Selecciona exactamente {n_p - 1} proteína(s) adicional(es) para continuar (faltan {faltan}).")

        if st.button("➕ Añadir Mixta", disabled=(faltan != 0)):
            nom = f"Mixta de {n_p} P. ({', '.join(prots)})"
            rec_mix = {"Bandejas de Aluminio (Llevar)": 1.0 * cant_m}
            for pr in prots:
                if "Pollo" in pr: val = 1.0
                elif "Congelada" in pr: val = 110.0
                else: val = 1.0
                rec_mix[pr] = rec_mix.get(pr, 0.0) + (val * cant_m)
            st.session_state.carrito.append({"tipo": "custom_mix", "item": nom, "cantidad": cant_m, "monto": monto_m, "receta": rec_mix})
            st.success(f"Añadido: {nom}")
            st.rerun()

    elif tipo_v == "Servicios Adicionales":
        serv = st.selectbox("Adicional:", [k for k, v in recetas_db.items() if v["categoria"] == "Servicios Adicionales"])
        cant = st.number_input("Cantidad:", min_value=1.0, max_value=CANTIDAD_MAX_LINEA, value=1.0)
        monto = st.number_input("Precio ($):", min_value=0.0, max_value=PRECIO_MAX_LINEA, value=min(recetas_db[serv]["precio_usd"] * cant, PRECIO_MAX_LINEA))
        if st.button("➕ Añadir"):
            st.session_state.carrito.append({"tipo": "plato", "item": serv, "cantidad": cant, "monto": monto})
            st.success(f"Añadido: {cant}x {serv}")
            st.rerun()

    else:
        directos = [k for k, v in inventario.items() if v["categoria"] in ["Bebidas", "Chucherías"]]
        prod = st.selectbox("Producto:", directos)
        cant = st.number_input("Cantidad:", min_value=1.0, max_value=CANTIDAD_MAX_LINEA, value=1.0)
        monto = st.number_input("Precio ($):", min_value=0.0, max_value=PRECIO_MAX_LINEA, value=min(inventario[prod]["precio_usd"] * cant, PRECIO_MAX_LINEA))
        if st.button("➕ Añadir"):
            st.session_state.carrito.append({"tipo": "insumo", "item": prod, "cantidad": cant, "monto": monto})
            st.success(f"Añadido: {cant}x {prod}")
            st.rerun()

    st.divider()
    if st.session_state.carrito:
        st.dataframe(pd.DataFrame([{"Producto": i["item"], "Cant.": i["cantidad"], "Subtotal ($)": i["monto"]} for i in st.session_state.carrito]), use_container_width=True)
        total = sum(i["monto"] for i in st.session_state.carrito)
        st.markdown(f"### 💰 Total: {total:.2f} $  *(Bs. {total * tasa:,.2f})*")

        if st.button("🗑️ Vaciar Lista"):
            st.session_state.carrito = []
            st.rerun()

        metodo = st.selectbox("Método de pago:", ["Digital (Pago Móvil / Punto)", "Físico (Bolívares)", "Físico (Dólares)", "🎁 Cortesía"])
        if st.button("✅ Facturar y Descontar", type="primary"):
            reqs = {}
            for i in st.session_state.carrito:
                if i["tipo"] == "plato":
                    for k, v in recetas_db[i["item"]]["ingredientes"].items():
                        reqs[k] = reqs.get(k, 0) + (v * i["cantidad"])
                elif i["tipo"] == "custom_mix":
                    for k, v in i["receta"].items():
                        reqs[k] = reqs.get(k, 0) + v
                else:
                    reqs[i["item"]] = reqs.get(i["item"], 0) + i["cantidad"]

            try:
                db.descontar_stock_por_venta(reqs, usuario["nombre"])
            except ValueError as e:
                st.error(f"❌ {e}")
            else:
                for i in st.session_state.carrito: db.sumar_item_vendido(i["item"], i["cantidad"])
                if "Cortesía" not in metodo:
                    if "Digital" in metodo: db.sumar_total("Digital", total)
                    elif "Bolívares" in metodo: db.sumar_total("Bs", total * tasa)
                    else: db.sumar_total("USD", total)

                pedido_txt = ", ".join([f"{i['cantidad']}x {i['item']}" for i in st.session_state.carrito])
                db.registrar_venta(vendedor=usuario["nombre"], pedido=pedido_txt, monto=total if "Cortesía" not in metodo else 0.0, metodo=metodo)
                st.session_state.carrito = []
                st.success("✅ ¡Venta procesada con éxito!")
                st.rerun()
    else:
        st.info("La lista está vacía.")

# ================= VER INVENTARIO =================
elif menu == "Ver Inventario":
    if l_inv: st_lottie(l_inv, height=120)
    st.header("📦 Inventario Actual")
    mostrar_inventario_por_categoria(inventario, expandir_todo=True)

# ================= GESTIÓN INVENTARIO =================
elif menu == "Gestión de Inventario":
    if l_inv: st_lottie(l_inv, height=100)
    st.header("⚙️ Gestión de Almacén")

    tab_stock, tab_precio, tab_nuevo, tab_recetas = st.tabs(["📦 Ajustar Stock", "💲 Editar Precio", "🆕 Agregar Producto", "📝 Platos y Menú"])

    with tab_stock:
        prod = st.selectbox("Insumo:", list(inventario.keys()), key="prod_stock")
        cant = st.number_input("Cantidad a sumar/restar:", format="%.2f")
        motivo = st.text_input("Motivo del ajuste (ej. 'compra proveedor', 'merma'):")
        if st.button("Actualizar Stock"):
            if not motivo.strip(): st.error("❌ Indica un motivo para el ajuste.")
            else:
                db.ajustar_stock(prod, cant, usuario["nombre"], motivo.strip())
                st.success(f"✅ Stock de {prod} actualizado.")
                st.rerun()

    with tab_precio:
        prod_p = st.selectbox("Insumo:", list(inventario.keys()), key="prod_precio")
        st.caption(f"Precio actual: ${inventario[prod_p]['precio_usd']:.2f}")
        nuevo_precio = st.number_input("Nuevo precio ($):", min_value=0.0, value=float(inventario[prod_p]["precio_usd"]), format="%.2f")
        if st.button("Actualizar Precio"):
            db.actualizar_precio(prod_p, nuevo_precio, usuario["nombre"])
            st.success(f"✅ Precio actualizado a ${nuevo_precio:.2f}.")
            st.rerun()

    with tab_nuevo:
        categorias_existentes = sorted({v["categoria"] for v in inventario.values()})
        nombre_nuevo = st.text_input("Nombre del producto:")
        categoria_nueva = st.selectbox("Categoría:", categorias_existentes + ["➕ Nueva categoría..."])
        if categoria_nueva == "➕ Nueva categoría...": categoria_nueva = st.text_input("Nombre de la nueva categoría:")
        unidad_nueva = st.text_input("Unidad (ej. 'unidades', 'gramos (g)'):", value="unidades")
        stock_nuevo = st.number_input("Stock inicial:", min_value=0.0, format="%.2f")
        precio_nuevo = st.number_input("Precio ($):", min_value=0.0, format="%.2f")
        codigo_nuevo = st.text_input("Código de barras (opcional):")
        if st.button("Agregar Producto"):
            if not nombre_nuevo.strip() or not categoria_nueva.strip(): st.error("❌ Indica nombre y categoría.")
            elif nombre_nuevo in inventario: st.error(f"❌ '{nombre_nuevo}' ya existe.")
            else:
                db.agregar_item(nombre_nuevo.strip(), categoria_nueva.strip(), stock_nuevo, unidad_nueva.strip(), precio_nuevo, codigo_nuevo.strip())
                st.success(f"✅ Agregado al inventario.")
                st.rerun()
                
    with tab_recetas:
        st.subheader("Configurar Menú y Recetas")
        nombres_recetas = ["➕ Crear nuevo plato"] + list(recetas_db.keys())
        receta_sel = st.selectbox("Plato a editar:", nombres_recetas)

        if receta_sel == "➕ Crear nuevo plato":
            r_nombre = st.text_input("Nombre del plato:")
            r_cat = st.selectbox("Categoría:", ["Parrilla Personal", "Parrilla Familiar", "Bebidas", "Servicios Adicionales", "Comida", "Aves"])
            r_precio = st.number_input("Precio al público ($):", min_value=0.0, format="%.2f")
            r_ings = {}
        else:
            r_nombre = receta_sel
            st.text_input("Nombre del plato (No editable):", value=r_nombre, disabled=True)
            cats = ["Parrilla Personal", "Parrilla Familiar", "Bebidas", "Servicios Adicionales", "Comida", "Aves"]
            cat_actual = recetas_db[r_nombre]["categoria"]
            if cat_actual not in cats: cats.append(cat_actual)
            r_cat = st.selectbox("Categoría:", cats, index=cats.index(cat_actual))
            r_precio = st.number_input("Precio al público ($):", min_value=0.0, value=float(recetas_db[r_nombre]["precio_usd"]), format="%.2f")
            r_ings = recetas_db[r_nombre]["ingredientes"]

        st.write("**Ingredientes a descontar de inventario al vender:**")
        todos_insumos = list(inventario.keys())
        insumos_sel = st.multiselect("Selecciona los insumos (Puedes escribir para buscar):", todos_insumos, default=list(r_ings.keys()))

        nuevos_ings = {}
        if insumos_sel:
            for ins in insumos_sel:
                val_def = float(r_ings.get(ins, 1.0))
                nuevos_ings[ins] = st.number_input(f"Cantidad a descontar de '{ins}':", min_value=0.01, value=val_def, step=0.5, format="%.2f")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Guardar Plato", type="primary"):
                if not r_nombre.strip() or not nuevos_ings: st.error("❌ Indica un nombre y al menos un insumo a descontar.")
                else:
                    db.guardar_receta(r_nombre.strip(), r_cat, r_precio, nuevos_ings)
                    st.success(f"✅ Plato '{r_nombre}' guardado exitosamente.")
                    st.rerun()
        with c2:
            if receta_sel != "➕ Crear nuevo plato":
                if st.button("🗑️ Eliminar Plato"):
                    db.eliminar_receta(r_nombre)
                    st.warning(f"✅ Plato '{r_nombre}' eliminado del menú.")
                    st.rerun()

# ================= CIERRE Y ESTADÍSTICAS =================
elif menu in ["Cierre Diario", "Cierre y Estadísticas"]:
    if l_cie: st_lottie(l_cie, height=120)
    st.header("📊 Cierre de Caja y Estadísticas")
    fecha_sel = st.date_input("Fecha:", value=date.today())
    fecha_str = fecha_sel.isoformat()
    tasa_c = st.number_input("Tasa de Cierre (Bs/$):", min_value=0.0, value=36.50, format="%.2f")

    tabs_labels = ["Cierre de Dinero", "📈 Estadísticas (Top Ventas)"]
    if usuario["rol"] == "admin": tabs_labels.append("🕵️ Auditoría de Stock")
    tabs = st.tabs(tabs_labels)

    with tabs[0]:
        totales = db.obtener_totales(fecha_str)
        t_dig, t_bs, t_usd = totales["Digital"], totales["Bs"], totales["USD"]
        g_tot = t_usd + ((t_dig + t_bs) / tasa_c if tasa_c > 0 else 0)
        st.markdown(f"### 💵 Total Equivalente: {g_tot:.2f} $")
        c1, c2, c3 = st.columns(3)
        c1.metric("Digital (Bs)", f"{t_dig:,.2f}")
        c2.metric("Efectivo (Bs)", f"{t_bs:,.2f}")
        c3.metric("Efectivo ($)", f"{t_usd:,.2f}")
        st.divider()
        ventas_dia = db.obtener_ventas(fecha_str)
        if ventas_dia: st.dataframe(pd.DataFrame(ventas_dia), use_container_width=True)
        else: st.info("No hay ventas registradas para esta fecha.")

        st.divider()
        st.subheader("📦 Stock restante del inventario (ahora mismo)")
        mostrar_inventario_por_categoria(inventario)

    with tabs[1]:
        stats = db.obtener_estadisticas(fecha_str)
        if stats:
            df_st = pd.DataFrame(list(stats.items()), columns=["Producto", "Cantidad"]).set_index("Producto").sort_values("Cantidad", ascending=False)
            st.bar_chart(df_st)
            st.dataframe(df_st, use_container_width=True)
        else: st.info("Sin datos estadísticos aún para esta fecha.")

    if usuario["rol"] == "admin":
        with tabs[2]:
            auditoria = db.obtener_auditoria(200)
            if auditoria: st.dataframe(pd.DataFrame(auditoria), use_container_width=True)
            else: st.info("Sin movimientos de stock registrados aún.")