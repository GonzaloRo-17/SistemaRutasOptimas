import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from sistema_rutas_optimas import SistemaRutas
import networkx as nx
import matplotlib.pyplot as plt

sistema = SistemaRutas()

# --- RED BASE AUTOMÁTICA ---
def cargar_red_base():
    sistema.agregar_ciudad("CiudadA")
    sistema.agregar_ciudad("CiudadB")
    sistema.agregar_ciudad("CiudadC")
    sistema.conectar_ciudades("CiudadA", "CiudadB", 10, "asfalto", 15, 5.0)
    sistema.conectar_ciudades("CiudadB", "CiudadC", 20, "asfalto", 25, 7.0)
    sistema.conectar_ciudades("CiudadA", "CiudadC", 35, "trocha", 45, 4.5)

# --- FUNCIONES DE LA INTERFAZ ---
def normalizar(nombre):
    return nombre.strip().lower()

def mostrar(nombre):
    return sistema.etiquetas_ciudades.get(nombre, nombre)

def agregar_ciudad():
    nombre = simpledialog.askstring("Agregar ciudad", "Nombre de la ciudad:")
    if nombre:
        clave = normalizar(nombre)
        if clave in sistema.grafo:
            messagebox.showerror("Error", "La ciudad ya existe.")
        else:
            sistema.etiquetas_ciudades[clave] = nombre.strip()
            sistema.agregar_ciudad(clave)
            messagebox.showinfo("Éxito", f"Ciudad '{nombre}' agregada.")

def editar_ciudad():
    actual = simpledialog.askstring("Editar ciudad", "Nombre actual de la ciudad:")
    nuevo = simpledialog.askstring("Nuevo nombre", "Nuevo nombre de la ciudad:")
    if actual and nuevo:
        clave_actual = normalizar(actual)
        clave_nuevo = normalizar(nuevo)
        if clave_actual in sistema.grafo:
            nx.relabel_nodes(sistema.grafo, {clave_actual: clave_nuevo}, copy=False)
            sistema.etiquetas_ciudades[clave_nuevo] = nuevo.strip()
            if clave_actual in sistema.etiquetas_ciudades:
                del sistema.etiquetas_ciudades[clave_actual]
            messagebox.showinfo("Éxito", f"Ciudad '{actual}' renombrada a '{nuevo}'.")
        else:
            messagebox.showerror("Error", "Ciudad no encontrada.")

def conectar_ciudades():
    c1 = simpledialog.askstring("Ciudad 1", "Nombre de la primera ciudad:")
    c2 = simpledialog.askstring("Ciudad 2", "Nombre de la segunda ciudad:")
    if c1 and c2:
        c1, c2 = normalizar(c1), normalizar(c2)
        if c1 not in sistema.grafo or c2 not in sistema.grafo:
            messagebox.showerror("Error", "Una o ambas ciudades no existen.")
            return
        try:
            d = float(simpledialog.askstring("Distancia", "Distancia (km):"))
            t = int(simpledialog.askstring("Tiempo", "Tiempo (min):"))
            costo = float(simpledialog.askstring("Costo", "Costo (S/):"))
            tipo = simpledialog.askstring("Tipo de ruta", "Tipo (ej. asfalto, trocha):") or "asfalto"
            sistema.conectar_ciudades(c1, c2, d, tipo, t, costo)
            messagebox.showinfo("Éxito", f"Ruta conectada entre {mostrar(c1)} y {mostrar(c2)}.")
        except:
            messagebox.showerror("Error", "Datos inválidos")

def editar_ruta():
    c1 = simpledialog.askstring("Ciudad 1", "Nombre de la primera ciudad:")
    c2 = simpledialog.askstring("Ciudad 2", "Nombre de la segunda ciudad:")
    if c1 and c2:
        c1, c2 = normalizar(c1), normalizar(c2)
        if not sistema.grafo.has_edge(c1, c2):
            messagebox.showerror("Error", "Ruta no encontrada.")
            return
        try:
            d = float(simpledialog.askstring("Nueva distancia", "Distancia (km):"))
            t = int(simpledialog.askstring("Nuevo tiempo", "Tiempo (min):"))
            costo = float(simpledialog.askstring("Nuevo costo", "Costo (S/):"))
            tipo = simpledialog.askstring("Nuevo tipo de ruta", "Tipo (ej. asfalto, trocha):") or "asfalto"
            sistema.grafo[c1][c2].update({"distancia": d, "tiempo": t, "costo": costo, "tipo": tipo})
            messagebox.showinfo("Éxito", f"Ruta entre {mostrar(c1)} y {mostrar(c2)} actualizada.")
        except:
            messagebox.showerror("Error", "Datos inválidos")

def mostrar_mapa():
    mapa_texto = ""
    for c1, c2, datos in sistema.grafo.edges(data=True):
        estado = "ACTIVA" if datos.get("activa", True) else "INACTIVA"
        mapa_texto += f"{mostrar(c1)} → {mostrar(c2)} ({datos['tipo']}, {datos['distancia']}km, {datos['tiempo']}min, S/{datos['costo']}, {estado})\n"
    if not mapa_texto:
        mapa_texto = "No hay rutas registradas."
    messagebox.showinfo("Mapa de rutas", mapa_texto)

def ver_mapa_grafico(ruta_optima=None):
    pos = nx.spring_layout(sistema.grafo, seed=42)
    plt.figure(figsize=(10, 6))
    plt.title("Mapa de Red de Rutas")

    nx.draw_networkx_nodes(sistema.grafo, pos, node_color="lightblue", node_size=700)
    labels = {n: mostrar(n) for n in sistema.grafo.nodes()}
    nx.draw_networkx_labels(sistema.grafo, pos, labels=labels, font_size=10)

    activas = [(u, v) for u, v, d in sistema.grafo.edges(data=True) if d.get("activa", True)]
    inactivas = [(u, v) for u, v, d in sistema.grafo.edges(data=True) if not d.get("activa", True)]

    ruta_edges = []
    if ruta_optima and len(ruta_optima) > 1:
        ruta_edges = [(ruta_optima[i], ruta_optima[i+1]) for i in range(len(ruta_optima)-1)]

    nx.draw_networkx_edges(sistema.grafo, pos, edgelist=activas, edge_color='gray', width=1.5)
    nx.draw_networkx_edges(sistema.grafo, pos, edgelist=inactivas, style='dashed', edge_color='black')
    if ruta_edges:
        nx.draw_networkx_edges(sistema.grafo, pos, edgelist=ruta_edges, edge_color='red', width=3)

    etiquetas = {(u, v): f"{d['distancia']}km" for u, v, d in sistema.grafo.edges(data=True)}
    nx.draw_networkx_edge_labels(sistema.grafo, pos, edge_labels=etiquetas, font_size=8)

    plt.axis('off')
    plt.show()

def calcular_ruta():
    origen = simpledialog.askstring("Origen", "Ciudad de origen:")
    destino = simpledialog.askstring("Destino", "Ciudad de destino:")
    criterio = simpledialog.askstring("Criterio", "Criterio (distancia/tiempo/costo):") or "distancia"
    origen, destino = normalizar(origen), normalizar(destino)
    ruta, total = sistema.ruta_optima(origen, destino, criterio)
    if ruta:
        ruta_mostrada = [mostrar(c) for c in ruta]
        mensaje = f"Ruta óptima:\n{' → '.join(ruta_mostrada)}\nTotal: {total} ({criterio})"
        messagebox.showinfo("Ruta óptima", mensaje)
        if messagebox.askyesno("Simulación", "¿Deseas ver la simulación gráfica?"):
            sistema.simular_movimiento_grafico(ruta)
        else:
            ver_mapa_grafico(ruta_optima=ruta)

def guardar_red():
    archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if archivo:
        sistema.guardar_en_archivo(archivo)
        messagebox.showinfo("Guardado", f"Red guardada en {archivo}")

def cargar_red():
    archivo = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if archivo:
        sistema.cargar_desde_archivo(archivo)
        messagebox.showinfo("Cargado", f"Red cargada desde {archivo}")

# --- INTERFAZ GRÁFICA PRINCIPAL ---
ventana = tk.Tk()
ventana.title("Sistema de Rutas Óptimas")
ventana.geometry("400x500")

# Agregamos el diccionario de etiquetas a la clase
sistema.etiquetas_ciudades = {}

cargar_red_base()

btn1 = tk.Button(ventana, text="Agregar ciudad", command=agregar_ciudad)
btn2 = tk.Button(ventana, text="Conectar ciudades", command=conectar_ciudades)
btn3 = tk.Button(ventana, text="Editar ciudad", command=editar_ciudad)
btn4 = tk.Button(ventana, text="Editar ruta", command=editar_ruta)
btn5 = tk.Button(ventana, text="Mostrar mapa de rutas (texto)", command=mostrar_mapa)
btn6 = tk.Button(ventana, text="Ver red de rutas (gráfico)", command=lambda: ver_mapa_grafico())
btn7 = tk.Button(ventana, text="Calcular ruta óptima", command=calcular_ruta)
btn8 = tk.Button(ventana, text="Guardar red", command=guardar_red)
btn9 = tk.Button(ventana, text="Cargar red", command=cargar_red)
btn10 = tk.Button(ventana, text="Salir", command=ventana.quit)

for i, btn in enumerate([btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10]):
    btn.pack(pady=5, ipadx=10, ipady=3, fill="x", padx=20)

ventana.mainloop()
