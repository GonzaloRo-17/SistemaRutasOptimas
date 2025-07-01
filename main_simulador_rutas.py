import subprocess
import sys

# Verificar e instalar dependencias
for paquete in ["networkx", "matplotlib"]:
    try:
        __import__(paquete)
    except ImportError:
        print(f"Instalando: {paquete}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

from sistema_rutas_optimas import SistemaRutas

sistema = SistemaRutas()

def menu():
    print("\n=== Menú del Sistema de Rutas ===")
    print("1. Mostrar mapa de rutas")
    print("2. Calcular ruta óptima")
    print("3. Cerrar ruta")
    print("4. Reabrir ruta")
    print("5. Ver mapa visual")
    print("6. Guardar red a archivo")
    print("7. Cargar red desde archivo")
    print("8. Salir")

while True:
    menu()
    opcion = input("\nElige una opción: ").strip()

    if opcion == "1":
        sistema.mostrar_mapa()

    elif opcion == "2":
        criterio = input("Criterio (distancia/tiempo/costo): ").strip().lower()
        origen = input("Origen: ").strip()
        destino = input("Destino: ").strip()
        ruta, total = sistema.ruta_optima(origen, destino, criterio)
        if ruta:
            unidad = {"distancia": "km", "tiempo": "min", "costo": "S/"}
            print(f"\nRuta óptima: {' → '.join(ruta)}")
            print(f"Total: {total} {unidad.get(criterio, '')}")

            if input("\n¿Simular movimiento en consola? (s/n): ").strip().lower() == "s":
                sistema.simular_movimiento(ruta)
            if input("\n¿Mostrar movimiento en gráfico? (s/n): ").strip().lower() == "s":
                sistema.simular_movimiento_grafico(ruta)

    elif opcion == "3":
        c1 = input("Ciudad origen: ")
        c2 = input("Ciudad destino: ")
        sistema.cerrar_ruta(c1, c2)

    elif opcion == "4":
        c1 = input("Ciudad origen: ")
        c2 = input("Ciudad destino: ")
        sistema.abrir_ruta(c1, c2)

    elif opcion == "5":
        sistema.simular_movimiento_grafico([])  # Muestra solo la red sin animar ruta

    elif opcion == "6":
        archivo = input("Nombre del archivo a guardar (ej. red.json): ").strip()
        sistema.guardar_en_archivo(archivo)

    elif opcion == "7":
        archivo = input("Nombre del archivo a cargar (ej. red.json): ").strip()
        sistema.cargar_desde_archivo(archivo)

    elif opcion == "8":
        print("Saliendo del sistema...")
        break

    else:
        print("Opción no válida.")
