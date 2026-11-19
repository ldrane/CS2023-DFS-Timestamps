import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from manim import *
from visual import SceneWithTiming, txt, TEXT, SUB, BLUE_ACCENT

class S07Creditos(SceneWithTiming):
    OBJETIVO = 6.0
    def construct(self):
        titulo = txt("DFS Timestamps", 54, TEXT)
        curso = txt("CS2023 · Algoritmos y Estructuras de Datos · Grupo 8", 24, SUB)
        nombres = VGroup(*[txt(n, 26, BLUE_ACCENT) for n in (
            "Hurtado Vite, Mia Dayhana",
            "Medina Gago, Leonardo Jesus",
            "Sempertegui Landavere, Richard Andres")]).arrange(DOWN, buff=0.2)
        todo = VGroup(titulo, curso, nombres).arrange(DOWN, buff=0.5)
        self.animar(FadeIn(todo), segundos=1.2)
        self.pausa(4.0)
        self.completar()
