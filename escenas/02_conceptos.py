
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *
from visual import (
    SceneWithTiming, Grafico, cargar, vertex, cabecera, txt,
    POS_CARPETAS, FOLDERS,
    BG, PANEL, BORDER, TEXT, SUB, EDGE, BLUE_ACCENT, YELLOW, GREEN,
)


def ajustar_ancho(elemento, maximo):

    if elemento.width > maximo:
        elemento.scale_to_fit_width(maximo)
    return elemento


def comprobar_separacion(a, b, nombre_a, nombre_b, margen=0.14):

    separacion_x = (a.get_right()[0] + margen <= b.get_left()[0] or
                    b.get_right()[0] + margen <= a.get_left()[0])
    separacion_y = (a.get_top()[1] + margen <= b.get_bottom()[1] or
                    b.get_top()[1] + margen <= a.get_bottom()[1])
    if not (separacion_x or separacion_y):
        raise ValueError(
            f"Colision visual: {nombre_a} / {nombre_b}. "
            "Aumenta los margenes o reduce el contenido."
        )


def comprobar_dentro(contenido, caja, margen=0.30):

    if not (
        contenido.get_left()[0] >= caja.get_left()[0] + margen - 0.005
        and contenido.get_right()[0] <= caja.get_right()[0] - margen + 0.005
        and contenido.get_bottom()[1] >= caja.get_bottom()[1] + margen - 0.005
        and contenido.get_top()[1] <= caja.get_top()[1] - margen + 0.005
    ):
        raise ValueError("El contenido se sale de la tarjeta derecha.")


def comprobar_en_pantalla(objeto, nombre, margen=0.20):

    mitad_ancho = config.frame_width / 2
    mitad_alto = config.frame_height / 2
    if not (
        objeto.get_left()[0] >= -mitad_ancho + margen
        and objeto.get_right()[0] <= mitad_ancho - margen
        and objeto.get_bottom()[1] >= -mitad_alto + margen
        and objeto.get_top()[1] <= mitad_alto - margen
    ):
        raise ValueError(f"{nombre}: excede los margenes de la pantalla.")


def bloque_doble(titulo, descripcion, color=BLUE_ACCENT,
                 tam_titulo=22, tam_desc=19):

    a = txt(titulo, tam_titulo, color)
    b = txt(descripcion, tam_desc, SUB)
    return VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.12)


class S02Conceptos(SceneWithTiming):
    OBJETIVO = 43.0

    def construct(self):
        # --------------------------------------------------------------
        # 1. Datos REALES de la ejecución del DFS en C++.
        # --------------------------------------------------------------
        datos = cargar("grafo_carpetas.json")
        raiz_id = datos["raices"][0]
        raiz = vertex(datos, raiz_id)
        eventos = datos["eventos"]
        entradas = [e for e in eventos if e["tipo"] == "entrar"]
        salidas = [e for e in eventos if e["tipo"] == "salir"]
        entrada_raiz = next(e for e in entradas if e["u"] == raiz_id)
        salida_raiz = next(e for e in salidas if e["u"] == raiz_id)
        assert entrada_raiz["t"] == raiz["tin"]
        assert salida_raiz["t"] == raiz["tout"]
        assert salidas[-1]["u"] == raiz_id  # la raíz termina al final

        padres = {v["id"]: v["padre"] for v in datos["vertices"]}

        def id_arista_del_padre(hijo):
            padre = padres[hijo]
            coincidencias = [
                a["id"] for a in datos["aristas"]
                if (a["u"] == padre and a["v"] == hijo)
                or (a["u"] == hijo and a["v"] == padre)
            ]
            if len(coincidencias) != 1:
                raise ValueError(f"No hay una única arista de árbol para {hijo}")
            return coincidencias[0]

        # --------------------------------------------------------------
        # 2. Encabezado y separación explícita de las dos columnas.
        # --------------------------------------------------------------
        encabezado = cabecera(
            "Un grafo, un recorrido y dos tiempos", "02 · Conceptos"
        )
        header_line = encabezado[-1]

        # Rectángulo invisible: sirve únicamente como guía para la columna.
        zona_izquierda = Rectangle(
            width=config.frame_width * 0.50,
            height=config.frame_height * 0.66,
            stroke_opacity=0,
            fill_opacity=0,
        )
        zona_izquierda.next_to(header_line, DOWN, buff=0.36)
        zona_izquierda.to_edge(LEFT, buff=0.72)

        subtitulo = txt("Cada vértice representa una carpeta", 25, SUB)
        ajustar_ancho(subtitulo, zona_izquierda.width - 0.18)
        subtitulo.next_to(header_line, DOWN, buff=0.34)
        subtitulo.align_to(zona_izquierda, LEFT)

        # --------------------------------------------------------------
        # 3. Grafo de la izquierda: tamaño y posición subordinados a zona.
        # --------------------------------------------------------------
        grafo = Grafico(datos, POS_CARPETAS, etiquetas=FOLDERS, radio=0.32)
        arbol = grafo.grupo
        ajustar_ancho(arbol, min(config.frame_width * 0.50,
                                  zona_izquierda.width - 0.12))
        if arbol.height > config.frame_height * 0.47:
            arbol.scale_to_fit_height(config.frame_height * 0.47)
        arbol.next_to(subtitulo, DOWN, buff=0.50)
        arbol.align_to(zona_izquierda, LEFT)

        # Leyenda DEBAJO del grafo, no encima de las etiquetas de nodos.
        marcador_vertice = Circle(
            radius=0.075, stroke_width=2, stroke_color=BLUE_ACCENT,
            fill_opacity=1, fill_color=BLUE_ACCENT,
        )
        legend_vertice = VGroup(
            marcador_vertice, txt("Vértice = carpeta", 19, SUB)
        ).arrange(RIGHT, buff=0.15)

        marcador_arista = Line(LEFT * 0.14, RIGHT * 0.14,
                              stroke_width=3, color=EDGE)
        legend_arista = VGroup(
            marcador_arista, txt("Arista = conexión", 19, SUB)
        ).arrange(RIGHT, buff=0.15)

        leyenda = VGroup(legend_vertice, legend_arista).arrange(
            RIGHT, buff=0.45
        )
        ajustar_ancho(leyenda, zona_izquierda.width - 0.15)
        leyenda.next_to(arbol, DOWN, buff=0.33)
        leyenda.align_to(zona_izquierda, LEFT)

        cierre_izq = txt(
            "Un mismo vértice recibe dos marcas de tiempo.", 20, SUB
        )
        ajustar_ancho(cierre_izq, zona_izquierda.width - 0.20)
        cierre_izq.next_to(leyenda, DOWN, buff=0.36)
        cierre_izq.align_to(zona_izquierda, LEFT)

        # Si el conjunto excediera el margen inferior, comprimimos
        # proporcionalmente SOLO el grafo y recolocamos leyenda y cierre.
        margen_inferior = -config.frame_height / 2 + 0.50
        if cierre_izq.get_bottom()[1] < margen_inferior:
            exceso = margen_inferior - cierre_izq.get_bottom()[1]
            alto_disponible = arbol.height - exceso - 0.12
            if alto_disponible <= 0:
                raise ValueError("La columna del grafo no tiene altura suficiente")
            arbol.scale_to_fit_height(alto_disponible)
            arbol.next_to(subtitulo, DOWN, buff=0.50)
            arbol.align_to(zona_izquierda, LEFT)
            leyenda.next_to(arbol, DOWN, buff=0.33)
            leyenda.align_to(zona_izquierda, LEFT)
            cierre_izq.next_to(leyenda, DOWN, buff=0.36)
            cierre_izq.align_to(zona_izquierda, LEFT)

        # --------------------------------------------------------------
        # 4. Tarjeta derecha: debajo del subtítulo y margen derecho real.
        # --------------------------------------------------------------
        tarjeta = RoundedRectangle(
            width=4.40,
            height=4.74,
            corner_radius=0.21,
            stroke_color=BORDER,
            stroke_width=2,
            fill_color=PANEL,
            fill_opacity=0.98,
        )
        tarjeta.next_to(subtitulo, DOWN, buff=0.42)
        tarjeta.to_edge(RIGHT, buff=0.78)  # Algo desplazada hacia la izquierda.
        tarjeta.set_z_index(1)

        # Todo el contenido de la tarjeta se diseña como UN VGroup.
        bloque_grafo = bloque_doble(
            "TDA · GRAFO", "Vértices conectados por aristas", BLUE_ACCENT,
            tam_titulo=21, tam_desc=18
        )
        bloque_dfs = bloque_doble(
            "DFS · PROFUNDIDAD", "Explora una rama y retrocede", TEXT,
            tam_titulo=21, tam_desc=18
        )
        bloque_tin = bloque_doble(
            "ENTRADA · tin", f"Proyecto: tin = {entrada_raiz['t']}", YELLOW,
            tam_titulo=21, tam_desc=19
        )
        bloque_tout = bloque_doble(
            "SALIDA · tout", f"Proyecto: tout = {salida_raiz['t']}", GREEN,
            tam_titulo=21, tam_desc=19
        )
        bloque_intervalo = bloque_doble(
            "INTERVALO RESULTANTE",
            f"Proyecto = [{raiz['tin']}, {raiz['tout']}]",
            BLUE_ACCENT, tam_titulo=19, tam_desc=22
        )
        bloques = [bloque_grafo, bloque_dfs,
                   bloque_tin, bloque_tout, bloque_intervalo]

        margen_interno = 0.35
        ancho_util = tarjeta.width - 2 * margen_interno
        alto_util = tarjeta.height - 2 * margen_interno
        for bloque in bloques:
            ajustar_ancho(bloque, ancho_util)
        contenido = VGroup(*bloques).arrange(
            DOWN, aligned_edge=LEFT, buff=0.28
        )
        ajustar_ancho(contenido, ancho_util)
        if contenido.height > alto_util:
            contenido.scale_to_fit_height(alto_util)
        contenido.move_to(tarjeta.get_center())
        contenido.set_z_index(3)

        # --------------------------------------------------------------
        # 5. Checks de colisión y encuadre PREVIOS a la animación.
        # --------------------------------------------------------------
        comprobar_separacion(encabezado, subtitulo, "encabezado", "subtítulo")
        comprobar_separacion(encabezado, tarjeta, "encabezado", "tarjeta")
        comprobar_separacion(subtitulo, tarjeta, "subtítulo", "tarjeta")
        comprobar_separacion(subtitulo, arbol, "subtítulo", "grafo")
        comprobar_separacion(arbol, tarjeta, "grafo", "tarjeta", margen=0.28)
        comprobar_separacion(arbol, leyenda, "grafo", "leyenda")
        comprobar_separacion(leyenda, cierre_izq, "leyenda", "cierre")
        comprobar_separacion(cierre_izq, tarjeta, "cierre", "tarjeta", margen=0.28)
        comprobar_dentro(contenido, tarjeta, margen=0.30)
        for uno, dos in zip(bloques, bloques[1:]):
            comprobar_separacion(uno, dos, "bloques de la tarjeta", "bloques de la tarjeta",
                                margen=0.10)
        for obj, nombre in [
            (encabezado, "Encabezado"),
            (subtitulo, "Subtítulo"),
            (arbol, "Grafo"),
            (leyenda, "Leyenda"),
            (cierre_izq, "Cierre izquierdo"),
            (tarjeta, "Tarjeta"),
        ]:
            comprobar_en_pantalla(obj, nombre)

        # --------------------------------------------------------------
        # 6. Animaciones. Recorremos las ramas según eventos REALES.
        #    Orden de entrada obtenido del JSON, nunca a mano.
        #    Duración exacta: 43.0 s (locución separada).
        # --------------------------------------------------------------
        self.animar(FadeIn(encabezado), segundos=1.2)
        self.pausa(2.1)
        self.animar(FadeIn(subtitulo), segundos=1.0)
        self.pausa(1.0)
        self.animar(FadeIn(arbol), segundos=2.4)
        self.pausa(1.8)
        self.animar(FadeIn(leyenda), segundos=1.0)
        self.pausa(1.2)

        self.animar(FadeIn(tarjeta), FadeIn(bloque_grafo), segundos=1.2)
        self.pausa(2.6)
        self.animar(FadeIn(bloque_dfs), segundos=1.2)
        self.pausa(3.0)

        self.animar(
            FadeIn(bloque_tin),
            grafo.colorear_nodo(raiz_id, YELLOW),
            segundos=1.2,
        )
        self.pausa(2.8)

        # Presentación resumida del DFS; en escena 03 se ve CADA evento.
        # Aquí las aristas que se destacan son exclusivamente aristas de
        # árbol (padres) de la implementación C++.
        pasos_ramas = [
            AnimationGroup(
                grafo.colorear_arista(id_arista_del_padre(e["u"]),
                                     BLUE_ACCENT, grosor=5),
                grafo.colorear_nodo(e["u"], BLUE_ACCENT),
                lag_ratio=0,
            )
            for e in entradas if e["u"] != raiz_id
        ]
        self.animar(LaggedStart(*pasos_ramas, lag_ratio=0.22), segundos=3.2)
        self.pausa(2.0)

        self.animar(
            FadeIn(bloque_tout),
            grafo.colorear_nodo(raiz_id, GREEN),
            segundos=1.2,
        )
        self.pausa(3.4)
        self.animar(FadeIn(bloque_intervalo), segundos=1.2)
        self.pausa(5.5)
        self.animar(FadeIn(cierre_izq), segundos=1.1)
        self.pausa(1.7)
        self.completar()
