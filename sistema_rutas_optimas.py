import networkx as nx
import matplotlib.pyplot as plt
import json
import time

class SistemaRutas:
    def __init__(self):
        self.grafo = nx.Graph()
        self.etiquetas_ciudades = {}  # nombre_normalizado -> nombre_original

    def normalizar(self, nombre):
        return nombre.strip().lower()

    def agregar_ciudad(self, nombre):
        clave = self.normalizar(nombre)
        self.grafo.add_node(clave)
        self.etiquetas_ciudades[clave] = nombre.strip()

    def conectar_ciudades(self, ciudad1, ciudad2, distancia, tipo, tiempo, costo):
        c1, c2 = self.normalizar(ciudad1), self.normalizar(ciudad2)
        self.grafo.add_edge(c1, c2,
                            distancia=distancia,
                            tipo=tipo,
                            tiempo=tiempo,
                            costo=costo,
                            activa=True)

    def mostrar_mapa(self):
        print("\nMapa actual de rutas:")
        for c1, c2, datos in self.grafo.edges(data=True):
            estado = "ACTIVA" if datos.get("activa", True) else "INACTIVA"
            nombre1 = self.etiquetas_ciudades.get(c1, c1)
            nombre2 = self.etiquetas_ciudades.get(c2, c2)
            print(f"{nombre1} ↔ {nombre2} [{datos['tipo']} | {datos['distancia']} km | {datos['tiempo']} min | S/ {datos['costo']} | {estado}]")

    def cerrar_ruta(self, ciudad1, ciudad2):
        c1, c2 = self.normalizar(ciudad1), self.normalizar(ciudad2)
        if self.grafo.has_edge(c1, c2):
            self.grafo[c1][c2]['activa'] = False

    def abrir_ruta(self, ciudad1, ciudad2):
        c1, c2 = self.normalizar(ciudad1), self.normalizar(ciudad2)
        if self.grafo.has_edge(c1, c2):
            self.grafo[c1][c2]['activa'] = True

    def ruta_optima(self, origen, destino, criterio="distancia"):
        c1, c2 = self.normalizar(origen), self.normalizar(destino)
        grafo_filtrado = nx.Graph()
        for u, v, datos in self.grafo.edges(data=True):
            if datos.get("activa", True):
                grafo_filtrado.add_edge(u, v, **datos)

        if c1 not in grafo_filtrado or c2 not in grafo_filtrado:
            print("Error: ciudad no existe o no está conectada.")
            return None, None

        try:
            ruta = nx.dijkstra_path(grafo_filtrado, c1, c2, weight=criterio)
            total = nx.dijkstra_path_length(grafo_filtrado, c1, c2, weight=criterio)
            return ruta, total
        except nx.NetworkXNoPath:
            print("No hay ruta disponible entre esas ciudades.")
            return None, None

    def simular_movimiento(self, ruta, velocidad=1.0):
        if not ruta or len(ruta) < 2:
            print("Ruta no válida para simular.")
            return

        print("\n🚌 Iniciando simulación de movimiento:")
        for i in range(len(ruta) - 1):
            origen = ruta[i]
            destino = ruta[i + 1]
            datos = self.grafo[origen][destino]
            tiempo_min = datos['tiempo']
            print(f"\nViajando de {self.etiquetas_ciudades.get(origen, origen)} a {self.etiquetas_ciudades.get(destino, destino)}...")
            for t in range(0, tiempo_min + 1, max(1, tiempo_min // 10)):
                print(f"⏱️ Tiempo transcurrido: {t} min", end='\r')
                time.sleep(0.2 * velocidad)
            print(f"✅ Llegó a {self.etiquetas_ciudades.get(destino, destino)}")
        print("\n🎉 Vehículo llegó a destino final.")

    def simular_movimiento_grafico(self, ruta, velocidad=1.0):
        if not ruta or len(ruta) < 2:
            print("Ruta no válida para simular.")
            return

        pos = nx.spring_layout(self.grafo, seed=42)
        plt.ion()
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.title("Simulación de Movimiento de Vehículo", fontsize=14)

        for i in range(len(ruta)):
            ax.clear()

            colores = []
            for nodo in self.grafo.nodes():
                if nodo == ruta[i]:
                    colores.append("red")
                elif nodo in ruta[:i]:
                    colores.append("green")
                else:
                    colores.append("lightgray")

            etiquetas = {n: self.etiquetas_ciudades.get(n, n) for n in self.grafo.nodes()}
            nx.draw_networkx_nodes(self.grafo, pos, node_size=700, node_color=colores, ax=ax)
            nx.draw_networkx_labels(self.grafo, pos, labels=etiquetas, font_size=10, font_color='black', ax=ax)

            activas = [(u, v) for u, v, d in self.grafo.edges(data=True) if d.get("activa", True)]
            inactivas = [(u, v) for u, v, d in self.grafo.edges(data=True) if not d.get("activa", True)]

            nx.draw_networkx_edges(self.grafo, pos, edgelist=activas, edge_color='gray', width=1.5, ax=ax)
            nx.draw_networkx_edges(self.grafo, pos, edgelist=inactivas, style="dashed", edge_color="black", width=1, ax=ax)

            etiquetas_aristas = {(u, v): f"{d['distancia']}km" for u, v, d in self.grafo.edges(data=True)}
            nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=etiquetas_aristas, font_size=8, ax=ax)

            ciudad_actual = self.etiquetas_ciudades.get(ruta[i], ruta[i])
            ax.set_title(f"Moviéndose hacia: {ciudad_actual}", fontsize=12)
            plt.axis('off')
            plt.pause(0.8 * velocidad)

        print("\n🚗 Vehículo ha llegado a su destino.")
        plt.ioff()
        plt.show()

    def guardar_en_archivo(self, ruta_archivo):
        datos = {
            "ciudades": [
                {"clave": clave, "nombre": nombre}
                for clave, nombre in self.etiquetas_ciudades.items()
            ],
            "rutas": []
        }
        for u, v, d in self.grafo.edges(data=True):
            datos["rutas"].append({
                "ciudad1": u,
                "ciudad2": v,
                "distancia": d["distancia"],
                "tipo": d["tipo"],
                "tiempo": d["tiempo"],
                "costo": d["costo"],
                "activa": d.get("activa", True)
            })
        with open(ruta_archivo, "w") as f:
            json.dump(datos, f, indent=4)

    def cargar_desde_archivo(self, ruta_archivo):
        try:
            with open(ruta_archivo, "r") as f:
                datos = json.load(f)
            self.grafo.clear()
            self.etiquetas_ciudades.clear()
            for ciudad in datos["ciudades"]:
                clave = ciudad["clave"]
                nombre = ciudad["nombre"]
                self.grafo.add_node(clave)
                self.etiquetas_ciudades[clave] = nombre
            for ruta in datos["rutas"]:
                self.grafo.add_edge(
                    ruta["ciudad1"], ruta["ciudad2"],
                    distancia=ruta["distancia"],
                    tipo=ruta["tipo"],
                    tiempo=ruta["tiempo"],
                    costo=ruta["costo"],
                    activa=ruta.get("activa", True)
                )
        except FileNotFoundError:
            print(f"Archivo {ruta_archivo} no encontrado.")
        except Exception as e:
            print(f"Error al cargar archivo: {e}")

