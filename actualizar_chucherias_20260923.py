"""
Aplica el conteo físico de "Chucherías" que reportó el vendedor (23-sep-2026)
a la base de datos real (villa_marina.db).

- Los productos que ya existían en el catálogo (Galletas Oreo, Doritos
  (Grande), Tip Top) se actualizan con fijar_stock/actualizar_precio.
- Los productos nuevos se agregan con agregar_item.
- Caramelos y Chupetas venían en bolívares (100bs y 300bs); se convirtieron
  a dólares usando la tasa 950 Bs/$ que se mencionó ese mismo día. Si la
  tasa real fue otra, corrige el precio después desde "Editar Precio" en
  la app (busca 'Caramelos' o 'Chupetas').

Ejecuta esto UNA SOLA VEZ, desde la misma carpeta donde está villa_marina.db:

    python actualizar_chucherias_20260923.py
"""
from database import init_db, fijar_stock, agregar_item, actualizar_precio

USUARIO_REGISTRO = "sistema (conteo físico 2026-09-23)"
TASA_ASUMIDA = 950.0  # Bs por $, para Caramelos y Chupetas — confirmar con Adán

# Productos que YA existían en el catálogo con otro nombre/precio
EXISTENTES = {
    "Galletas Oreo": {"stock": 7, "precio": 2.00},
    "Doritos (Grande)": {"stock": 8, "precio": 5.00},
    "Tip Top": {"stock": 42, "precio": 1.50},
}

# Productos nuevos: nombre -> (stock, precio_usd)
NUEVOS = {
    "Estela": (5, 2.00),
    "Galletas rellenas": (2, 1.20),
    "Maxi coco": (16, 1.20),
    "Charmy": (10, 2.00),
    "Anternados": (9, 1.50),
    "Potata": (3, 1.50),
    "Choco chips": (35, 0.60),
    "Escureto": (12, 2.00),
    "Palitos": (12, 1.20),
    "Flaquito": (9, 1.20),
    "Ruffles Grande": (6, 5.00),
    "Pepito Grande": (7, 3.50),
    "Bilo": (4, 5.00),
    "De Todito": (2, 5.00),
    "Natu Chips": (9, 1.50),
    "Lays": (6, 1.50),
    "Rakety": (12, 1.20),
    "Combito": (11, 1.50),
    "Doritos (Pequeño)": (4, 1.50),
    "Chetos": (24, 1.20),
    "Cheese Tree": (9, 1.50),
    "Kraker": (26, 0.60),
    "Hony": (27, 0.60),
    "Club Social": (35, 0.60),
    "Universal": (4, 3.00),
    "Chimon": (4, 1.00),
    "Caramelos": (241, round(100 / TASA_ASUMIDA, 4)),
    "Chupetas": (2, round(300 / TASA_ASUMIDA, 4)),
}


def main():
    init_db()

    print("== Actualizando productos ya existentes ==")
    for item, datos in EXISTENTES.items():
        try:
            fijar_stock(item, datos["stock"], USUARIO_REGISTRO, motivo="conteo físico 2026-09-23")
            actualizar_precio(item, datos["precio"], USUARIO_REGISTRO)
            print(f"  ✅ {item}: stock={datos['stock']}, precio=${datos['precio']:.2f}")
        except ValueError as e:
            print(f"  ⚠️  {item}: {e} (revisa el nombre exacto en tu inventario)")

    print("\n== Agregando productos nuevos ==")
    for item, (stock, precio) in NUEVOS.items():
        agregar_item(item, categoria="Chucherías", stock=stock, unidad="unidades", precio_usd=precio)
        print(f"  ✅ {item}: stock={stock}, precio=${precio:.2f}")

    print("\nListo. Revisa 'Ver Inventario' en la app para confirmar que todo quedó bien.")
    print(f"(Caramelos y Chupetas se convirtieron de Bs a $ usando tasa {TASA_ASUMIDA} — ajústalo si no era la tasa correcta.)")


if __name__ == "__main__":
    main()
