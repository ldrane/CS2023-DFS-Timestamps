
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    Scene, Text, VGroup, Circle, Line, RoundedRectangle, FadeIn,
    BLUE, RIGHT, LEFT, UP, DOWN, WHITE, config,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datos"

BG = "#0B1220"
PANEL = "#162238"
BORDER = "#324762"
TEXT = "#F1F5FC"
SUB = "#B8C8DF"
MUTED = "#71839C"
EDGE = "#4B607E"
BLUE_ACCENT = "#64B5F6"
YELLOW = "#FFD166"      # tin: entrada
GREEN = "#56E0BD"       # tout: salida
RED = "#FB7185"         # arista de retroceso
PURPLE = "#C5A4FF"

FONT = "Arial"
MONO = "Consolas"

FOLDERS = {
    1: "Proyecto", 2: "Código", 3: "Algoritmos", 4: "Pruebas",
    5: "Datos", 6: "Imágenes", 7: "Informe",
}

# Posiciones autorales para que la gráfica sea legible; la topología y los
# timestamps, en cambio, siempre proceden del JSON emitido por el algoritmo.
POS_CARPETAS = {
    1: (-3.3, 1.55), 2: (-5.2, 0.32), 3: (-6.05, -1.20),
    4: (-4.33, -1.20), 5: (-2.35, 0.32), 6: (-2.35, -1.20),
    7: (-0.25, 0.32),
}
POS_CLASE = {
    1: (-3.15, 1.52), 2: (-5.15, 0.15), 3: (-5.27, -1.4),
    5: (-3.15, -1.55), 4: (-1.05, 0.10), 6: (-1.30, -1.50),
    7: (0.36, -1.45),
}
POS_DESC = {
    1: (-5.65, 0.60), 2: (-4.45, 1.65), 3: (-4.05, -0.55),
    4: (-2.18, 1.45), 5: (-2.55, -0.40), 6: (-0.90, 0.22),
    7: (0.10, -0.90), 8: (0.65, 1.64),
}


def cargar(nombre: str) -> dict:
    ruta = DATA / nombre
    if not ruta.is_file():
        raise FileNotFoundError(
            f"Falta {ruta}. Ejecuta primero scripts/generar_datos.ps1."
        )
    with ruta.open(encoding="utf-8") as f:
        return json.load(f)


def vertex(d: dict, identificador: int) -> dict:
    return next(x for x in d["vertices"] if x["id"] == identificador)


def consulta_ancestro(d: dict, u: int, v: int) -> bool:
    return next(x["resultado"] for x in d["consultas_ancestro"]
                if x["u"] == u and x["v"] == v)


def txt(cadena: str, size: int = 29, color: str = TEXT, mono: bool = False):
    return Text(str(cadena), font=MONO if mono else FONT,
                font_size=size, color=color)


def cabecera(titulo: str, capitulo: str):
    cab = txt(titulo, 35)
    if cab.width > 9.6:
        cab.scale_to_fit_width(9.6)
    cab.to_edge(UP, buff=0.28).to_edge(LEFT, buff=0.58)
    etiqueta = txt(capitulo.upper(), 18, BLUE_ACCENT).to_edge(UP, buff=0.48).to_edge(RIGHT, buff=0.61)
    regla = Line(np.array([-6.1, 2.58, 0]), np.array([6.1, 2.58, 0]),
                 color=BORDER, stroke_width=2)
    return VGroup(cab, etiqueta, regla)


def panel(cx=3.85, cy=-0.12, w=4.45, h=4.80):
    return RoundedRectangle(
        corner_radius=0.23, width=w, height=h,
        stroke_width=2, stroke_color=BORDER,
        fill_color=PANEL, fill_opacity=0.98,
    ).move_to(np.array([cx, cy, 0]))


class SceneWithTiming(Scene):
    """Contabiliza segundos de video y completa el objetivo con pausas.

    Los tiempos son deliberados para editar la voz en un programa externo.
    """
    OBJETIVO = 40.0

    def setup(self):
        super().setup()
        self.camera.background_color = BG
        self._segundos = 0.0

    def animar(self, *animaciones, segundos=1.0):
        if animaciones:
            self.play(*animaciones, run_time=segundos)
            self._segundos += segundos

    def pausa(self, segundos=1.0):
        if segundos > 0.0001:
            self.wait(segundos)
            self._segundos += segundos

    def completar(self):
        restante = self.OBJETIVO - self._segundos
        if restante < -0.02:
            raise ValueError(
                f"La escena {type(self).__name__} dura {self._segundos:.1f}s; "
                f"excede el objetivo de {self.OBJETIVO}s."
            )
        self.pausa(max(0, restante))


class Grafico:
    """Dibuja exclusivamente los nodos/aristas presentes en el JSON."""

    def __init__(self, d: dict, posiciones: dict,
                 etiquetas: dict | None = None, radio=0.34):
        self.d = d
        self.posiciones = {u: np.array([x, y, 0.0]) for u, (x, y) in posiciones.items()}
        assert set(self.posiciones) == set(range(1, d["n"]+1))
        self.edges = {}
        self.nodes = {}
        self.labels = {}

        for ar in d["aristas"]:
            u, v = ar["u"], ar["v"]
            linea = Line(self.posiciones[u], self.posiciones[v],
                          color=EDGE, stroke_width=4)
            self.edges[ar["id"]] = linea

        for v in range(1, d["n"] + 1):
            circulo = Circle(radius=radio, stroke_width=3,
                             stroke_color=BLUE_ACCENT,
                             fill_color=PANEL, fill_opacity=1).move_to(self.posiciones[v])
            numero = txt(str(v), 29).move_to(self.posiciones[v])
            self.nodes[v] = VGroup(circulo, numero)
            if etiquetas is not None:
                nombre = txt(etiquetas[v], 17, SUB).next_to(circulo, DOWN, buff=0.08)
                self.labels[v] = nombre

        self.grupo = VGroup(*self.edges.values(), *self.nodes.values(),
                            *self.labels.values())

    def colorear_nodo(self, u: int, color: str):
        return self.nodes[u][0].animate.set_fill(color, opacity=0.86).set_stroke(color, width=3)

    def colorear_arista(self, id_arista: int, color: str, grosor: int=6):
        return self.edges[id_arista].animate.set_stroke(color=color, width=grosor)

    def colorear_conjunto(self, vertices, color: str):
        return [self.colorear_nodo(u, color) for u in vertices]
