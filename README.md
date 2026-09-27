# Villa Marina - Control de Ventas

## Qué cambió respecto a la versión anterior

1. **Base de datos compartida (SQLite, `villa_marina.db`).** Antes, cada
   vendedor tenía su propio inventario/ventas en memoria (`st.session_state`),
   así que no se veían los cambios entre sí y todo se perdía al reiniciar el
   servidor. Ahora inventario, ventas, totales, estadísticas y auditoría se
   guardan en un archivo SQLite que comparten todos los usuarios.
2. **Contraseñas fuera del código.** Ya no existen en texto plano en `app.py`.
   Se crean con `setup_usuarios.py` y se guardan como hash (PBKDF2 + salt) en
   la base de datos.
3. **Bug del escáner corregido.** Antes, la misma foto del código de barras se
   volvía a procesar en cada actualización de la página. Ahora solo se procesa
   una vez por foto.
4. **Auditoría de stock.** Cada ajuste manual o descuento por venta queda
   registrado con usuario, fecha/hora, ítem, cantidad y motivo (pestaña
   "🕵️ Auditoría de Stock", solo visible para el rol `admin`).
5. **Límites de precio y cantidad** en las líneas del carrito, para evitar
   errores de tecleo al facturar.
6. **Cierre y estadísticas por fecha**, en vez de un acumulado que solo se
   podía "reiniciar" perdiendo el historial: ahora puedes elegir cualquier día
   y ver sus ventas/estadísticas por separado.

## Cómo arrancar

```bash
pip install -r requirements.txt

# 1) Crear los usuarios (una sola vez, o cuando necesites agregar/resetear alguno)
python setup_usuarios.py

# 2) Correr la app
streamlit run app.py
```

Si despliegas en Streamlit Community Cloud, sube también `packages.txt`
(necesario para que `pyzbar` pueda leer códigos de barras).

## Segunda ronda de ajustes (requerimientos originales de la primera versión)

- **Pollo unificado**: "Pollo Entero" y "Porción de Pollo (1 Cuarto)" ahora son
  un solo ítem, `Pollo (Cuartos)`, donde 1 entero = 4 cuartos. Si ya tenías
  `villa_marina.db` con los dos ítems viejos, la app los fusiona automáticamente
  la primera vez que arranca (sin perder stock) y lo deja anotado en la
  auditoría. De paso, ahora sí puedes vender un pollo entero crudo desde
  "Control de Ventas" — antes no existía esa opción en ninguna pantalla.
- **Gramajes de las mixtas**: se mantiene el reparto del total entre las
  proteínas elegidas (330g repartidos entre 3 da 110g cada una, que coincide
  con tu propio ejemplo). No se agregó peso fijo por proteína ni proteínas
  nuevas (lomito, carne de puerco), tal como me confirmaste.
- **Cierre diario integral**: la pestaña "Cierre de Dinero" ahora muestra,
  sin cambiar de pestaña, los totales, el historial de ventas del día Y el
  stock restante del inventario (agrupado por categoría).
- **Categorización visual**: tanto "Ver Inventario" como el stock dentro del
  cierre ahora se muestran agrupados por categoría (Carnes 🥩, Bebidas 🥤,
  Chucherías 🍪, etc.) en secciones desplegables, en vez de una tabla plana.

Sigue pendiente (no lo pediste explícitamente todavía, pero quedó anotado):
un módulo para crear/editar recetas desde la app sin tocar código — hoy
`RECETAS` en `app.py` sigue siendo fijo.

## Notas

- `villa_marina.db` se crea automáticamente la primera vez que corres
  `setup_usuarios.py` o `app.py`. Haz respaldo de ese archivo periódicamente
  (o mejor, prográmalo automáticamente) — es donde vive todo tu negocio.
- Las recetas (`RECETAS` en `app.py`) siguen siendo un diccionario fijo en el
  código, igual que antes, porque no había forma de editarlas desde la app.
  Si más adelante quieres editarlas desde la interfaz, se pueden mover a su
  propia tabla en `database.py` con el mismo patrón que usa `inventario`.
