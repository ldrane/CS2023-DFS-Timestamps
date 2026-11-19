from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manim import *
from visual import (
    SceneWithTiming, Grafico, cabecera, cargar, consulta_ancestro,
    vertex, txt, POS_CARPETAS, FOLDERS,
    BG, PANEL, BORDER, TEXT, SUB, MUTED, EDGE,
    BLUE_ACCENT, YELLOW, GREEN, RED, PURPLE,
)


def limitar(mob, ancho=None, alto=None):
    if ancho is not None and mob.width > ancho:
        mob.scale_to_fit_width(ancho)
    if alto is not None and mob.height > alto:
        mob.scale_to_fit_height(alto)
    return mob


def comprobar_separacion(a, b, descripcion, margen=0.15):
    separado_x = (a.get_right()[0] + margen <= b.get_left()[0]
                   or b.get_right()[0] + margen <= a.get_left()[0])
    separado_y = (a.get_top()[1] + margen <= b.get_bottom()[1]
                   or b.get_top()[1] + margen <= a.get_bottom()[1])
    if not (separado_x or separado_y):
        raise ValueError(f"COLISIÓN: {descripcion}")


def comprobar_dentro(objeto, region, descripcion, margen=0.12):
    if not (
        objeto.get_left()[0] >= region.get_left()[0] + margen - 0.01
        and objeto.get_right()[0] <= region.get_right()[0] - margen + 0.01
        and objeto.get_top()[1] <= region.get_top()[1] - margen + 0.01
        and objeto.get_bottom()[1] >= region.get_bottom()[1] + margen - 0.01
    ):
        raise ValueError(f"Fuera de su región: {descripcion}")


def comprobar_pantalla(objeto, descripcion, margen=0.17):
    mitad_w = config.frame_width / 2
    mitad_h = config.frame_height / 2
    if not (
        objeto.get_left()[0] >= -mitad_w + margen
        and objeto.get_right()[0] <= mitad_w - margen
        and objeto.get_top()[1] <= mitad_h - margen
        and objeto.get_bottom()[1] >= -mitad_h + margen
    ):
        raise ValueError(f"Fuera de pantalla: {descripcion}")


def verificar_bloques_vgroup(bloques, descripcion):
    """Controla que filas de texto contiguas no se superpongan."""
    for anterior, siguiente in zip(bloques, bloques[1:]):
        comprobar_separacion(anterior, siguiente, descripcion, margen=0.09)


def texto_ajustado(cadena, region, tam=21, color=TEXT, mono=False):
    """Texto legible: se prepara en base al ancho real de su zona."""
    objeto = txt(cadena, tam, color, mono=mono)
    limitar(objeto, ancho=region.width - 0.12)
    return objeto


def tarjeta_intervalos(nombre_a, a, nombre_b, b, n, color_b):

    fondo = RoundedRectangle(
        width=4.38, height=1.60, corner_radius=0.14,
        stroke_color=BORDER, stroke_width=1.3,
        fill_color=BG, fill_opacity=0.78,
    )

    eje = Line(LEFT * 1.91, RIGHT * 1.91,
               color=EDGE, stroke_width=2).move_to(fondo)
    marcas = VGroup()
    for t in range(1, 2 * n + 1):
        p = eje.point_from_proportion((t - 1) / (2 * n - 1))
        marcas.add(Dot(point=p, color=MUTED, radius=0.026))

    def barra(v, color, desplazamiento):
        p1 = eje.point_from_proportion((v["tin"] - 1) / (2 * n - 1))
        p2 = eje.point_from_proportion((v["tout"] - 1) / (2 * n - 1))
        linea = Line(p1, p2, stroke_width=10, color=color)
        linea.shift(desplazamiento)  # Desplazamiento relativo al eje.
        return linea

    barra_a = barra(a, YELLOW, UP * 0.27)
    barra_b = barra(b, color_b, DOWN * 0.27)

    nom_a = txt(f"{nombre_a} [{a['tin']}, {a['tout']}]", 17, YELLOW)
    nom_b = txt(f"{nombre_b} [{b['tin']}, {b['tout']}]", 17, color_b)
    nom_a.next_to(barra_a, UP, buff=0.11)
    nom_b.next_to(barra_b, DOWN, buff=0.11)

    # Si una etiqueta es muy larga, se acota al espacio del gráfico.
    limitar(nom_a, ancho=fondo.width - 0.38)
    limitar(nom_b, ancho=fondo.width - 0.38)

    grupo = VGroup(fondo, eje, marcas, barra_a, barra_b, nom_a, nom_b)
    # Las etiquetas forman parte del gráfico y deben caber en su fondo.
    comprobar_dentro(VGroup(eje, marcas, barra_a, barra_b, nom_a, nom_b),
                     fondo, "Gráfico de intervalos", margen=0.085)
    return grupo


def pagina_consulta(nombre_a, a, nombre_b, b, n, resultado):
    """Una página con pregunta, escala y comprobación de desigualdades."""
    tono = GREEN if resultado else RED
    pregunta = txt(f"¿{nombre_a} contiene a {nombre_b}?", 22, TEXT)
    grafico = tarjeta_intervalos(
        nombre_a, a, nombre_b, b, n, GREEN if resultado else RED,
    )

    comparar_entrada = txt(
        f"tin:    {a['tin']} ≤ {b['tin']}    {'SÍ' if a['tin'] <= b['tin'] else 'NO'}",
        21, YELLOW if a['tin'] <= b['tin'] else RED, mono=True,
    )
    comparar_salida = txt(
        f"tout:  {b['tout']} ≤ {a['tout']}    {'SÍ' if b['tout'] <= a['tout'] else 'NO'}",
        21, GREEN if b['tout'] <= a['tout'] else RED, mono=True,
    )
    bloque_comparacion = VGroup(comparar_entrada, comparar_salida).arrange(
        DOWN, aligned_edge=LEFT, buff=0.16,
    )
    respuesta = txt(
        "SÍ: intervalo contenido" if resultado else "NO: intervalo fuera de Código",
        23, tono,
    )

    # Separación explícita; cada fase se puede animar individualmente.
    bloques = [pregunta, grafico, bloque_comparacion, respuesta]
    pagina = VGroup(*bloques).arrange(DOWN, buff=0.18)
    return pagina, bloques


def pagina_subarbol(nombre, a, tamano, nombres):
    titulo = txt(f"¿Qué contiene el subárbol de {nombre}?", 22)
    explicacion = txt("Incluimos el propio nodo y sus descendientes", 18, SUB)

    intervalo = txt(f"{nombre}: [{a['tin']}, {a['tout']}]", 25, YELLOW)
    formula = txt(
        f"({a['tout']} - {a['tin']} + 1) / 2 = {tamano}",
        27, PURPLE, mono=True,
    )

    nombre_cajas = []
    for nombre_carpeta in nombres:
        etiqueta = txt(nombre_carpeta, 17, TEXT)
        caja = RoundedRectangle(
            width=max(1.16, etiqueta.width + 0.23),
            height=0.44, corner_radius=0.10,
            stroke_color=BLUE_ACCENT, stroke_width=1.4,
            fill_color="#253956", fill_opacity=1,
        )
        etiqueta.move_to(caja)
        nombre_cajas.append(VGroup(caja, etiqueta))
    fichas = VGroup(*nombre_cajas).arrange(RIGHT, buff=0.11)
    respuesta = txt(f"{tamano} carpetas en este subárbol", 24, GREEN)

    bloques = [titulo, explicacion, intervalo, formula, fichas, respuesta]
    pagina = VGroup(*bloques).arrange(DOWN, buff=0.25)
    return pagina, bloques


class S04Aplicacion(SceneWithTiming):
    OBJETIVO = 55.0

    def construct(self):
        # 1. Datos REALES de la implementación iterativa de C++.
        datos = cargar("grafo_carpetas.json")
        n = datos["n"]
        codigo_id, pruebas_id, imagenes_id = 2, 4, 6
        codigo = vertex(datos, codigo_id)
        pruebas = vertex(datos, pruebas_id)
        imagenes = vertex(datos, imagenes_id)
        assert consulta_ancestro(datos, codigo_id, pruebas_id) is True
        assert consulta_ancestro(datos, codigo_id, imagenes_id) is False
        tamano = next(q["tamano"] for q in datos["consultas_subarbol"]
                      if q["u"] == codigo_id)

        padres = {v["id"]: v["padre"] for v in datos["vertices"]}
        hijos_directos = [v["id"] for v in datos["vertices"]
                          if v["padre"] == codigo_id]
        descendientes = [v["id"] for v in datos["vertices"]
                         if (codigo["tin"] <= v["tin"]
                             and v["tout"] <= codigo["tout"])]
        assert len(descendientes) == tamano == 3
        assert set(hijos_directos) == {3, 4}

        # 2. Encabezado; columna izquierda = texto+árbol+nota.
        encabezado = cabecera(
            "¿Para qué sirven los timestamps?", "04 · Aplicación real",
        )
        linea_cabecera = encabezado[-1]
        zona_izquierda = Rectangle(
            width=config.frame_width * 0.47,
            height=config.frame_height * 0.69,
            stroke_opacity=0, fill_opacity=0,
        )
        zona_izquierda.next_to(linea_cabecera, DOWN, buff=0.34)
        zona_izquierda.to_edge(LEFT, buff=0.72)

        subtitulo = txt("Volvemos al árbol de carpetas", 24, SUB)
        limitar(subtitulo, ancho=zona_izquierda.width - 0.15)
        subtitulo.next_to(linea_cabecera, DOWN, buff=0.32)
        subtitulo.align_to(zona_izquierda, LEFT)

        grafo = Grafico(datos, POS_CARPETAS, etiquetas=FOLDERS, radio=0.32)
        arbol = grafo.grupo
        limitar(arbol, ancho=min(zona_izquierda.width - 0.08,
                                 config.frame_width * 0.52), alto=3.65)
        arbol.next_to(subtitulo, DOWN, buff=0.46)
        arbol.align_to(zona_izquierda, LEFT)

        caja_mensaje = RoundedRectangle(
            width=zona_izquierda.width - 0.10, height=0.82,
            corner_radius=0.17, stroke_color=BORDER, stroke_width=1.3,
            fill_color=PANEL, fill_opacity=0.93,
        )
        caja_mensaje.next_to(arbol, DOWN, buff=0.32)
        caja_mensaje.align_to(zona_izquierda, LEFT)

        mensaje = txt("Buscamos una relación entre carpetas.", 19, SUB)
        limitar(mensaje, ancho=caja_mensaje.width - 0.35,
                alto=caja_mensaje.height - 0.22)
        mensaje.move_to(caja_mensaje)
        mensaje.set_z_index(3)

        def otro_mensaje(texto, color=SUB):
            m = txt(texto, 19, color)
            limitar(m, ancho=caja_mensaje.width - 0.35,
                    alto=caja_mensaje.height - 0.22)
            m.move_to(mensaje)
            return m

        # 3. Panel DERECHO: colocado *debajo* del subtítulo, nunca sobre él.
        tarjeta = RoundedRectangle(
            width=5.20, height=4.88, corner_radius=0.23,
            stroke_color=BORDER, stroke_width=2,
            fill_color=PANEL, fill_opacity=0.98,
        )
        tarjeta.next_to(subtitulo, DOWN, buff=0.43)
        tarjeta.to_edge(RIGHT, buff=0.70)
        tarjeta.set_z_index(1)

        titulo_tarjeta = txt("COMPARAR INTERVALOS", 21, BLUE_ACCENT)
        limitar(titulo_tarjeta, ancho=tarjeta.width - 0.70)
        titulo_tarjeta.next_to(tarjeta.get_top(), DOWN, buff=0.34)
        titulo_tarjeta.align_to(tarjeta, LEFT).shift(RIGHT * 0.35)
        titulo_tarjeta.set_z_index(3)

        zona_contenido = Rectangle(
            width=tarjeta.width - 0.62,
            height=tarjeta.height - 1.20,
            stroke_opacity=0, fill_opacity=0,
        )
        zona_contenido.next_to(titulo_tarjeta, DOWN, buff=0.21)
        zona_contenido.align_to(tarjeta, LEFT).shift(RIGHT * 0.31)

        # 4. Tres páginas autosuficientes dentro de la misma tarjeta.
        pag_positiva, pos_bloques = pagina_consulta(
            FOLDERS[codigo_id], codigo, FOLDERS[pruebas_id], pruebas,
            n, consulta_ancestro(datos, codigo_id, pruebas_id),
        )
        pag_negativa, neg_bloques = pagina_consulta(
            FOLDERS[codigo_id], codigo, FOLDERS[imagenes_id], imagenes,
            n, consulta_ancestro(datos, codigo_id, imagenes_id),
        )
        pag_subarbol, sub_bloques = pagina_subarbol(
            FOLDERS[codigo_id], codigo, tamano,
            [FOLDERS[u] for u in descendientes],
        )

        for pagina in (pag_positiva, pag_negativa, pag_subarbol):
            limitar(pagina, ancho=zona_contenido.width - 0.24,
                    alto=zona_contenido.height - 0.20)
            pagina.move_to(zona_contenido)
            pagina.set_z_index(3)
            comprobar_dentro(pagina, zona_contenido, "Página de consulta", 0.07)

        # 5. Preparar una marca para el subárbol real del nodo Código.
        elementos_subarbol = VGroup(*(
            grafo.nodes[u] for u in descendientes
        ), *(
            grafo.labels[u] for u in descendientes
        ))
        marco_subarbol = SurroundingRectangle(
            elementos_subarbol, color=PURPLE, buff=0.24,
            corner_radius=0.17, stroke_width=3,
        )
        marco_subarbol.set_z_index(3)

        aristas_subarbol = [a["id"] for a in datos["aristas"]
                            if (a["u"] == codigo_id and a["v"] in hijos_directos)
                            or (a["v"] == codigo_id and a["u"] in hijos_directos)]
        assert len(aristas_subarbol) == len(hijos_directos)

        # 6. Validaciones geométricas antes del primer play().
        comprobar_separacion(encabezado, subtitulo, "cabecera / subtítulo")
        comprobar_separacion(subtitulo, arbol, "subtítulo / grafo")
        comprobar_separacion(subtitulo, tarjeta, "subtítulo / panel")
        comprobar_separacion(arbol, caja_mensaje, "grafo / mensaje")
        comprobar_separacion(arbol, tarjeta, "grafo / panel", 0.24)
        comprobar_separacion(caja_mensaje, tarjeta, "mensaje / panel", 0.20)
        comprobar_dentro(titulo_tarjeta, tarjeta, "Título de la tarjeta", 0.24)
        comprobar_dentro(zona_contenido, tarjeta, "Región de tarjeta", 0.15)
        comprobar_dentro(mensaje, caja_mensaje, "Mensaje", 0.12)
        for objeto, nombre in (
            (encabezado, "encabezado"), (subtitulo, "subtítulo"),
            (arbol, "árbol"), (caja_mensaje, "nota izquierda"),
            (tarjeta, "tarjeta"), (marco_subarbol, "marco subárbol"),
        ):
            comprobar_pantalla(objeto, nombre)
        comprobar_separacion(marco_subarbol, tarjeta, "marco subárbol / tarjeta")
        for bloques in (pos_bloques, neg_bloques, sub_bloques):
            verificar_bloques_vgroup(bloques, "Bloques internos")

        # ============================================================
        # 7. ANIMACIÓN (55 SEGUNDOS, diseñada para voz en off).
        # ============================================================
        # 00:00-00:08: conexión con las escenas anteriores.
        self.animar(FadeIn(encabezado), segundos=1.0)
        self.animar(FadeIn(subtitulo), segundos=0.9)
        self.animar(Create(arbol), segundos=2.0)
        self.animar(FadeIn(tarjeta), FadeIn(titulo_tarjeta), segundos=1.1)
        self.animar(FadeIn(caja_mensaje), FadeIn(mensaje), segundos=0.8)
        self.pausa(2.2)

        # 00:08-00:24: POSITIVO, Pruebas dentro de Código.
        self.animar(
            grafo.colorear_nodo(codigo_id, YELLOW),
            grafo.colorear_nodo(pruebas_id, GREEN),
            FadeIn(pos_bloques[0]), segundos=1.2,
        )
        self.pausa(1.7)
        self.animar(FadeIn(pos_bloques[1]), segundos=1.8)
        self.pausa(2.8)
        self.animar(FadeIn(pos_bloques[2]), segundos=1.1)
        self.pausa(2.4)
        self.animar(
            FadeIn(pos_bloques[3]),
            Transform(mensaje, otro_mensaje("Las dos desigualdades se cumplen.", GREEN)),
            segundos=1.2,
        )
        self.pausa(3.8)

        # 00:24-00:38: NEGATIVO, Imágenes fuera de Código.
        self.animar(
            *[FadeOut(b) for b in pos_bloques],
            grafo.colorear_nodo(pruebas_id, PANEL),
            grafo.colorear_nodo(imagenes_id, RED),
            Transform(mensaje, otro_mensaje("Probemos con otra carpeta.", SUB)),
            segundos=0.9,
        )
        self.animar(FadeIn(neg_bloques[0]), segundos=0.9)
        self.pausa(1.6)
        self.animar(FadeIn(neg_bloques[1]), segundos=1.5)
        self.pausa(2.4)
        self.animar(FadeIn(neg_bloques[2]), segundos=1.2)
        self.pausa(1.8)
        self.animar(
            FadeIn(neg_bloques[3]),
            Transform(mensaje, otro_mensaje("Imágenes está en otra rama.", RED)),
            segundos=1.2,
        )
        self.pausa(2.5)

        # 00:38-00:55: TAMAÑO DEL SUBÁRBOL.
        self.animar(
            *[FadeOut(b) for b in neg_bloques],
            grafo.colorear_nodo(imagenes_id, PANEL),
            segundos=0.9,
        )
        self.animar(FadeIn(sub_bloques[0]), segundos=1.1)
        self.pausa(1.5)
        self.animar(
            grafo.colorear_nodo(codigo_id, YELLOW),
            grafo.colorear_nodo(3, GREEN),
            grafo.colorear_nodo(pruebas_id, GREEN),
            *[grafo.colorear_arista(i, PURPLE, grosor=5)
              for i in aristas_subarbol],
            FadeIn(sub_bloques[1]),
            segundos=1.6,
        )
        self.pausa(2.4)
        self.animar(FadeIn(sub_bloques[2]), FadeIn(sub_bloques[3]), segundos=1.2)
        self.pausa(2.2)
        self.animar(
            Create(marco_subarbol),
            FadeIn(sub_bloques[4]), FadeIn(sub_bloques[5]),
            Transform(mensaje, otro_mensaje("Código + Algoritmos + Pruebas = 3", GREEN)),
            segundos=1.6,
        )
        self.pausa(4.5)
        self.completar()
