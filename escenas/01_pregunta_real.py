
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *
from visual import *


def comprobar_sin_colision(a, b, descripcion, margen=0.12):

    izquierda_de = a.get_right()[0] + margen <= b.get_left()[0]
    derecha_de = b.get_right()[0] + margen <= a.get_left()[0]
    debajo_de = a.get_top()[1] + margen <= b.get_bottom()[1]
    encima_de = b.get_top()[1] + margen <= a.get_bottom()[1]
    if not (izquierda_de or derecha_de or debajo_de or encima_de):
        raise ValueError(
            f"Elementos demasiado próximos o superpuestos: {descripcion}. "
            "Ajusta el ancho de las zonas o los márgenes."
        )


def comprobar_dentro_de_caja(contenido, caja, margen=0.30):
    """Evita que letras o números salgan del panel lateral."""
    if not (
        contenido.get_left()[0] >= caja.get_left()[0] + margen
        and contenido.get_right()[0] <= caja.get_right()[0] - margen
        and contenido.get_top()[1] <= caja.get_top()[1] - margen
        and contenido.get_bottom()[1] >= caja.get_bottom()[1] + margen
    ):
        raise ValueError("El texto sobrepasa el área útil de la tarjeta derecha.")


def ajustar_ancho(elemento, ancho_maximo):

    if elemento.width > ancho_maximo:
        elemento.scale_to_fit_width(ancho_maximo)
    return elemento


class S01PreguntaReal(SceneWithTiming):
    OBJETIVO = 38.0

    def construct(self):
        # 1. Datos reales provenientes del DFS de C++, no de pasos ficticios.
        datos = cargar("grafo_carpetas.json")
        assert consulta_ancestro(datos, 2, 4) is True
        codigo = vertex(datos, 2)
        pruebas = vertex(datos, 4)

        # 2. Encabezado. Su última pieza es la línea divisoria real.
        encabezado = cabecera(
            "¿Cómo sabe un sistema dónde está una carpeta?",
            "01 · Problema real",
        )
        header_line = encabezado[-1]

        # 3. Región izquierda INVISIBLE: referencia espacial, no dibujada.
        zona_izquierda = Rectangle(
            width=config.frame_width * 0.51,
            height=config.frame_height * 0.67,
            stroke_opacity=0,
            fill_opacity=0,
        )
        zona_izquierda.next_to(header_line, DOWN, buff=0.35)
        zona_izquierda.to_edge(LEFT, buff=0.67)

        # 4. Subtítulo: pertenece SOLO a la columna izquierda.
        subtitulo = txt(
            "Imagina esta estructura de un proyecto de software",
            25,
            SUB,
        )
        ajustar_ancho(subtitulo, zona_izquierda.width - 0.24)
        subtitulo.next_to(header_line, DOWN, buff=0.36)
        subtitulo.align_to(zona_izquierda, LEFT)

        # 5. Grafo: se adapta a la columna izquierda y queda bajo el subtítulo.
        grafo = Grafico(datos, POS_CARPETAS, etiquetas=FOLDERS, radio=0.32)
        arbol = grafo.grupo
        ancho_arbol = min(config.frame_width * 0.52, zona_izquierda.width - 0.16)
        ajustar_ancho(arbol, ancho_arbol)
        if arbol.height > config.frame_height * 0.53:
            arbol.scale_to_fit_height(config.frame_height * 0.53)
        arbol.next_to(subtitulo, DOWN, buff=0.55)
        arbol.align_to(zona_izquierda, LEFT)

        # 6. Recuadro derecho: bajo el subtítulo, con margen derecho constante.
        # Importante: aquí NO se usan cx/cy absolutos.
        tarjeta = RoundedRectangle(
            width=4.20,
            height=4.65,
            corner_radius=0.20,
            stroke_color=BORDER,
            stroke_width=2,
            fill_color=PANEL,
            fill_opacity=0.98,
        )
        tarjeta.next_to(subtitulo, DOWN, buff=0.35)
        tarjeta.to_edge(RIGHT, buff=0.77)  # Un poco más a la izquierda.
        tarjeta.set_z_index(1)

        # 7. Contenido interno. Todo se distribuye con arrange()/next_to().
        limite_texto = tarjeta.width - 0.72

        titulo_consulta = txt("CONSULTA DE EJEMPLO", 18, BLUE_ACCENT)
        pregunta = txt("¿Código contiene\na Pruebas?", 24, TEXT)
        bloque_pregunta = VGroup(titulo_consulta, pregunta)
        bloque_pregunta.arrange(DOWN, aligned_edge=LEFT, buff=0.17)

        nombre_codigo = txt("2  ·  Código", 23, YELLOW)
        nombre_pruebas = txt("4  ·  Pruebas", 23, BLUE_ACCENT)
        bloque_nombres = VGroup(nombre_codigo, nombre_pruebas)
        bloque_nombres.arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        titulo_tiempos = txt("TIEMPOS DE ENTRADA Y SALIDA", 16, SUB)
        intervalo_codigo = txt(
            f"Código  [{codigo['tin']}, {codigo['tout']}]",
            21, TEXT, mono=True,
        )
        intervalo_pruebas = txt(
            f"Pruebas [{pruebas['tin']}, {pruebas['tout']}]",
            21, TEXT, mono=True,
        )
        bloque_tiempos = VGroup(
            titulo_tiempos, intervalo_codigo, intervalo_pruebas
        )
        bloque_tiempos.arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        texto_resultado = txt("SÍ, está dentro de Código", 19, GREEN)
        explicacion = txt(
            f"[{codigo['tin']}, {codigo['tout']}] contiene [{pruebas['tin']}, {pruebas['tout']}]",
            18, SUB, mono=True,
        )
        bloque_respuesta = VGroup(texto_resultado, explicacion)
        bloque_respuesta.arrange(DOWN, aligned_edge=LEFT, buff=0.13)

        bloques = [
            bloque_pregunta, bloque_nombres, bloque_tiempos, bloque_respuesta
        ]
        for bloque in bloques:
            ajustar_ancho(bloque, limite_texto)

        contenido = VGroup(*bloques)
        contenido.arrange(DOWN, aligned_edge=LEFT, buff=0.27)
        ajustar_ancho(contenido, limite_texto)
        alto_maximo = tarjeta.height - 0.72
        if contenido.height > alto_maximo:
            contenido.scale_to_fit_height(alto_maximo)
        contenido.move_to(tarjeta.get_center())
        contenido.set_z_index(3)

        # 8. Verificaciones previas al render para detectar regresiones.
        comprobar_sin_colision(encabezado, subtitulo, "encabezado / subtítulo")
        comprobar_sin_colision(subtitulo, arbol, "subtítulo / árbol")
        comprobar_sin_colision(subtitulo, tarjeta, "subtítulo / tarjeta")
        comprobar_sin_colision(arbol, tarjeta, "árbol / tarjeta", margen=0.30)
        comprobar_dentro_de_caja(contenido, tarjeta, margen=0.29)
        for a, b in zip(bloques, bloques[1:]):
            comprobar_sin_colision(a, b, "secciones internas de tarjeta", margen=0.10)

        # 9. Animación. Se conserva el presupuesto de 38 s del guion original.
        self.animar(FadeIn(encabezado), segundos=1.2)
        self.pausa(2.0)

        self.animar(FadeIn(subtitulo), segundos=1.0)
        self.pausa(1.0)

        self.animar(FadeIn(arbol), segundos=3.0)
        self.pausa(6.0)

        self.animar(FadeIn(tarjeta), FadeIn(bloque_pregunta), segundos=1.4)
        self.animar(
            grafo.colorear_nodo(2, YELLOW),
            grafo.colorear_nodo(4, BLUE_ACCENT),
            segundos=1.1,
        )
        self.pausa(6.0)

        self.animar(FadeIn(bloque_nombres), segundos=1.2)
        self.pausa(4.0)

        self.animar(FadeIn(bloque_tiempos), segundos=1.5)
        self.pausa(3.0)

        self.animar(FadeIn(bloque_respuesta), segundos=1.4)
        self.pausa(3.0)
        self.completar()  # Completa los 38 segundos exactos.
