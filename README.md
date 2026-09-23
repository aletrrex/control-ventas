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

## Notas

- `villa_marina.db` se crea automáticamente la primera vez que corres
  `setup_usuarios.py` o `app.py`. Haz respaldo de ese archivo periódicamente
  (o mejor, prográmalo automáticamente) — es donde vive todo tu negocio.
- Las recetas (`RECETAS` en `app.py`) siguen siendo un diccionario fijo en el
  código, igual que antes, porque no había forma de editarlas desde la app.
  Si más adelante quieres editarlas desde la interfaz, se pueden mover a su
  propia tabla en `database.py` con el mismo patrón que usa `inventario`.
