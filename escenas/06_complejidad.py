
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manim import *
from visual import (
    SceneWithTiming, cabecera, cargar, txt,
    PANEL, BORDER, TEXT, SUB, BLUE_ACCENT, YELLOW, GREEN, PURPLE,
)


# -------------------------- DISEÑO SEGURO ---------------------------

def ajustar(mob: Mobject, zona: Mobject, px: float = 0.17, py: float = 0.10):
    """Limita las dimensiones del texto a su propia celda."""
    w = zona.width - 2 * px
    h = zona.height - 2 * py
    if w <= 0 or h <= 0:
        raise ValueError("Zona de texto sin espacio interior suficiente")
    if mob.width > w:
        mob.scale_to_fit_width(w)
    if mob.height > h:
        mob.scale_to_fit_height(h)
    return mob


def esta_dentro(mob: Mobject, caja: Mobject, nombre: str, pad: float = 0.10):
    eps = 0.018  # tolerancia para redondeo y anchura de trazos
    if not (
        mob.get_left()[0] >= caja.get_left()[0] + pad - eps
        and mob.get_right()[0] <= caja.get_right()[0] - pad + eps
        and mob.get_bottom()[1] >= caja.get_bottom()[1] + pad - eps
        and mob.get_top()[1] <= caja.get_top()[1] - pad + eps
    ):
        raise ValueError(
            f"{nombre} fuera de su zona: "
            f"contenido ({mob.get_left()[0]:.2f}, {mob.get_right()[0]:.2f}, "
            f"{mob.get_bottom()[1]:.2f}, {mob.get_top()[1]:.2f}) | "
            f"contenedor ({caja.get_left()[0]:.2f}, {caja.get_right()[0]:.2f}, "
            f"{caja.get_bottom()[1]:.2f}, {caja.get_top()[1]:.2f})"
        )


def no_chocan(a: Mobject, b: Mobject, descripcion: str, separacion=0.12):
    disj_x = (a.get_right()[0] + separacion <= b.get_left()[0]
              or b.get_right()[0] + separacion <= a.get_left()[0])
    disj_y = (a.get_top()[1] + separacion <= b.get_bottom()[1]
              or b.get_top()[1] + separacion <= a.get_bottom()[1])
    if not (disj_x or disj_y):
        raise ValueError(f"Hay colision entre {descripcion}")


def en_pantalla(mob: Mobject, descripcion: str, margen=0.18):
    limite_x = config.frame_width / 2 - margen
    limite_y = config.frame_height / 2 - margen
    if (mob.get_left()[0] < -limite_x or mob.get_right()[0] > limite_x
            or mob.get_bottom()[1] < -limite_y or mob.get_top()[1] > limite_y):
        raise ValueError(f"Fuera del encuadre: {descripcion}")


def ficha(etiqueta: str, dato: str, color: str):
    titulo = txt(etiqueta, 17, SUB)
    valor = txt(dato, 22, color, mono=True)
    contenido = VGroup(titulo, valor).arrange(RIGHT, buff=0.14)
    base = RoundedRectangle(
        width=max(1.55, contenido.width + 0.48), height=0.56,
        corner_radius=0.14, stroke_width=1.4,
        stroke_color=BORDER, fill_color=PANEL, fill_opacity=0.98,
    )
    ajustar(contenido, base, 0.16, 0.10)
    contenido.move_to(base)
    esta_dentro(contenido, base, f"ficha {etiqueta}", 0.09)
    return VGroup(base, contenido)


def fila_tabla(ancho: float, alto: float, operacion: str, costo: str,
               razon: str, color: str, cabecera_fila=False):
    """Un fondo + 3 celdas. Todas las posiciones son relativas a la fila."""
    bg = RoundedRectangle(
        width=ancho, height=alto, corner_radius=0.10,
        stroke_width=0 if cabecera_fila else 1.0,
        stroke_color="#344962",
        fill_color="#223956" if cabecera_fila else "#101C2E",
        fill_opacity=1.0,
    )

    # Zonas geométricas invisibles; sus anchos suman exactamente `ancho`.
    c1 = Rectangle(width=ancho * 0.395, height=alto,
                   stroke_opacity=0, fill_opacity=0)
    c2 = Rectangle(width=ancho * 0.195, height=alto,
                   stroke_opacity=0, fill_opacity=0)
    c3 = Rectangle(width=ancho * 0.410, height=alto,
                   stroke_opacity=0, fill_opacity=0)
    columnas = VGroup(c1, c2, c3).arrange(RIGHT, buff=0)
    columnas.move_to(bg)

    if cabecera_fila:
        t1 = txt(operacion, 18, BLUE_ACCENT)
        t2 = txt(costo, 18, BLUE_ACCENT)
        t3 = txt(razon, 18, BLUE_ACCENT)
    else:
        t1 = txt(operacion, 22, TEXT)
        t2 = txt(costo, 27, color, mono=True)
        t3 = txt(razon, 19, SUB)

    for j, (contenido, celda) in enumerate(zip((t1, t2, t3), columnas)):
        ajustar(contenido, celda, px=0.20, py=0.11)
        contenido.move_to(celda)
        if j != 1:
            contenido.align_to(celda, LEFT)
            contenido.shift(RIGHT * 0.20)
        esta_dentro(contenido, celda, f"celda {j+1}: {operacion}", 0.10)

    return VGroup(bg, t1, t2, t3)


# ------------------------------- ESCENA ------------------------------

class S06Complejidad(SceneWithTiming):
    OBJETIVO = 39.0

    def construct(self):
        # V y E se leen del grafo que ejecutó nuestro programa en C++.
        datos = cargar("grafo_clase.json")
        vertices = datos["n"]
        aristas = len(datos["aristas"])
        assert vertices == 7 and aristas == 8

        encabezado = cabecera("Complejidad de DFS con timestamps", "06 · Complejidad")
        linea = encabezado[-1]

        # A. FILA SUPERIOR: texto a la izquierda y dos cifras a la derecha.
        subtitulo = txt("¿Cuánto cuestan las operaciones vistas?", 24, SUB)
        subtitulo.next_to(linea, DOWN, buff=0.29)
        subtitulo.to_edge(LEFT, buff=0.84)

        v = ficha("V =", str(vertices), BLUE_ACCENT)
        e = ficha("E =", str(aristas), PURPLE)
        fichas = VGroup(v, e).arrange(RIGHT, buff=0.20)
        fichas.align_to(subtitulo, UP)
        fichas.to_edge(RIGHT, buff=0.84)

        ancho_disponible = fichas.get_left()[0] - subtitulo.get_left()[0] - 0.36
        if ancho_disponible <= 0:
            raise ValueError("No queda espacio entre subtitulo y fichas")
        if subtitulo.width > ancho_disponible:
            subtitulo.scale_to_fit_width(ancho_disponible)
        fila_superior = VGroup(subtitulo, fichas)

        # B. TABLA: el bloque completo está CENTRADO dentro del recuadro.
        # No se usa next_to(table.get_top()) para una sola fila.
        tabla = RoundedRectangle(
            width=11.96, height=3.54, corner_radius=0.18,
            stroke_width=2, stroke_color=BORDER,
            fill_color=PANEL, fill_opacity=0.98,
        )
        tabla.next_to(fila_superior, DOWN, buff=0.22)
        tabla.to_edge(LEFT, buff=(config.frame_width - tabla.width) / 2)
        tabla.set_z_index(-2)

        titulos = fila_tabla(11.48, 0.60, "OPERACIÓN", "TIEMPO",
                            "¿POR QUÉ?", BLUE_ACCENT, cabecera_fila=True)
        fila1 = fila_tabla(11.48, 0.76,
                           "DFS + tin y tout", "O(V + E)",
                           "Visita vértices y examina aristas", BLUE_ACCENT)
        fila2 = fila_tabla(11.48, 0.76,
                           "Consulta de ancestro", "O(1)",
                           "Compara los intervalos tin/tout", YELLOW)
        fila3 = fila_tabla(11.48, 0.76,
                           "Tamaño de subárbol", "O(1)",
                           "Calcula (tout - tin + 1) / 2", GREEN)

        contenido_tabla = VGroup(titulos, fila1, fila2, fila3)
        contenido_tabla.arrange(DOWN, buff=0.10)
        contenido_tabla.move_to(tabla)

        # C. NOTA DE ESPACIO. No mezclamos memoria y tiempo en la tabla.
        memoria = RoundedRectangle(
            width=tabla.width, height=0.66, corner_radius=0.14,
            stroke_width=1.4, stroke_color=BORDER,
            fill_color="#152841", fill_opacity=0.98,
        )
        memoria.next_to(tabla, DOWN, buff=0.18)
        memoria.align_to(tabla, LEFT)

        mem_label = txt("Espacio auxiliar del DFS", 19, SUB)
        mem_value = txt("O(V)", 24, PURPLE, mono=True)
        mem_why = txt("Pila y arreglos de marcas y padres", 18, TEXT)
        mem_texto = VGroup(mem_label, mem_value, mem_why).arrange(RIGHT, buff=0.26)
        ajustar(mem_texto, memoria, px=0.31, py=0.14)
        mem_texto.move_to(memoria)

        # D. MENSAJE FINAL.
        cierre = RoundedRectangle(
            width=tabla.width, height=0.72, corner_radius=0.14,
            stroke_width=1.6, stroke_color=BLUE_ACCENT,
            fill_color="#102B36", fill_opacity=0.98,
        )
        cierre.next_to(memoria, DOWN, buff=0.16)
        cierre.align_to(memoria, LEFT)
        mensaje = txt(
            "DFS recorre en O(V + E). Después, consultas con timestamps: O(1).",
            24, GREEN,
        )
        ajustar(mensaje, cierre, px=0.31, py=0.14)
        mensaje.move_to(cierre)

        # VALIDACIONES DE VERDAD: validamos objetos agrupados y fondos.
        esta_dentro(contenido_tabla, tabla, "todas las filas de la tabla", pad=0.16)
        esta_dentro(mem_texto, memoria, "nota de memoria", pad=0.12)
        esta_dentro(mensaje, cierre, "mensaje de cierre", pad=0.12)
        no_chocan(encabezado, fila_superior, "encabezado / subtitulo", 0.14)
        no_chocan(fila_superior, tabla, "subtitulo / tabla", 0.15)
        no_chocan(tabla, memoria, "tabla / memoria", 0.12)
        no_chocan(memoria, cierre, "memoria / cierre", 0.10)
        no_chocan(subtitulo, fichas, "subtitulo / cifras V y E", 0.22)
        for nombre, mob in [
            ("encabezado", encabezado), ("subtitulo y fichas", fila_superior),
            ("tabla", tabla), ("memoria", memoria), ("cierre", cierre),
        ]:
            en_pantalla(mob, nombre)

        # CRONOGRAMA. Total exacto: 39 segundos.
        # 00:00–00:08 · contexto y títulos de la tabla
        self.animar(FadeIn(encabezado), segundos=0.9)
        self.pausa(1.5)
        self.animar(FadeIn(subtitulo), FadeIn(v), FadeIn(e), segundos=1.1)
        self.pausa(1.6)
        self.animar(FadeIn(tabla), FadeIn(titulos[0]),
                    FadeIn(titulos[1]), FadeIn(titulos[2]), FadeIn(titulos[3]),
                    segundos=1.1)
        self.pausa(1.8)

        # 00:08–00:16 · coste del recorrido
        self.animar(*[FadeIn(m) for m in fila1], segundos=1.2)
        self.pausa(2.5)
        self.animar(Indicate(fila1[2], color=BLUE_ACCENT), segundos=1.0)
        self.pausa(3.3)

        # 00:16–00:22.5 · consulta de ancestro
        self.animar(*[FadeIn(m) for m in fila2], segundos=1.2)
        self.pausa(1.9)
        self.animar(Indicate(fila2[2], color=YELLOW), segundos=0.9)
        self.pausa(2.5)

        # 00:22.5–00:28.5 · tamaño del subárbol
        self.animar(*[FadeIn(m) for m in fila3], segundos=1.2)
        self.pausa(2.0)
        self.animar(Indicate(fila3[2], color=GREEN), segundos=1.0)
        self.pausa(1.8)

        # 00:28.5–00:33.3 · espacio auxiliar
        self.animar(FadeIn(memoria), FadeIn(mem_texto), segundos=1.0)
        self.pausa(3.8)

        # 00:33.3–00:39 · conclusión
        self.animar(FadeIn(cierre), FadeIn(mensaje), segundos=1.2)
        self.pausa(4.5)
        self.completar()
