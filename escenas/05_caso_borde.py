
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manim import *
from visual import (
    SceneWithTiming, Grafico, cabecera, cargar, vertex, txt,
    BG, PANEL, BORDER, TEXT, SUB, MUTED, EDGE,
    BLUE_ACCENT, YELLOW, GREEN, RED, PURPLE,
)


# -------------- Seguridad de márgenes y colisiones -----------------------

def ajustar(elemento, ancho=None, alto=None):
    if ancho is not None and elemento.width > ancho:
        elemento.scale_to_fit_width(ancho)
    if alto is not None and elemento.height > alto:
        elemento.scale_to_fit_height(alto)
    return elemento


def separados(a, b, nombre, separacion=0.11):

    apartados_x = (a.get_right()[0] + separacion <= b.get_left()[0]
                   or b.get_right()[0] + separacion <= a.get_left()[0])
    apartados_y = (a.get_top()[1] + separacion <= b.get_bottom()[1]
                   or b.get_top()[1] + separacion <= a.get_bottom()[1])
    if not (apartados_x or apartados_y):
        raise ValueError(f"COLISIÓN entre regiones: {nombre}")


def dentro(objeto, contenedor, nombre, padding=0.11):
    if not (
        objeto.get_left()[0] >= contenedor.get_left()[0] + padding - 0.005
        and objeto.get_right()[0] <= contenedor.get_right()[0] - padding + 0.005
        and objeto.get_top()[1] <= contenedor.get_top()[1] - padding + 0.005
        and objeto.get_bottom()[1] >= contenedor.get_bottom()[1] + padding - 0.005
    ):
        raise ValueError(f"Fuera de su zona: {nombre}")


def dentro_pantalla(objeto, nombre, margen=0.18):
    limite_x = config.frame_width / 2
    limite_y = config.frame_height / 2
    if not (
        objeto.get_left()[0] >= -limite_x + margen
        and objeto.get_right()[0] <= limite_x - margen
        and objeto.get_bottom()[1] >= -limite_y + margen
        and objeto.get_top()[1] <= limite_y - margen
    ):
        raise ValueError(f"Fuera de pantalla: {nombre}")


def estado_ajustado(frase, contenedor, color=TEXT, tam=22):
    objeto = txt(frase, tam, color)
    ajustar(objeto, ancho=contenedor.width - 0.54)
    return objeto


class S05CasoBorde(SceneWithTiming):
    OBJETIVO = 42.0

    def construct(self):
        # ---------------- Datos genuinos: C++ -> JSON -----------------
        datos = cargar("grafo_desconectado.json")
        eventos = datos["eventos"]
        vertices = {v["id"]: v for v in datos["vertices"]}
        raices = datos["raices"]
        assert raices == [1, 4, 8]
        assert datos["n"] == 8 and len(datos["aristas"]) == 6
        assert [e["u"] for e in eventos if e["tipo"] == "nuevo_arbol"] == raices

        # Cada componente se deriva del intervalo de su raíz y los timestamps
        # calculados por C++, sin suponer los resultados del recorrido.
        componentes = [
            [v for v in sorted(vertices)
             if vertices[r]["tin"] <= vertices[v]["tin"]
             and vertices[v]["tout"] <= vertices[r]["tout"]]
            for r in raices
        ]
        assert componentes == [[1, 2, 3], [4, 5, 6, 7], [8]]
        assert [(vertices[r]["tin"], vertices[r]["tout"]) for r in raices] == [
            (1, 6), (7, 14), (15, 16),
        ]
        numero_total = max(v["tout"] for v in vertices.values())
        assert numero_total == 2 * datos["n"] == 16

        # ---------------- Layout: encabezado y zonas ------------------
        header = cabecera(
            "¿Qué ocurre si el grafo está desconectado?", "05 · Caso borde",
        )
        linea = header[-1]

        zona_izq = Rectangle(
            width=7.55, height=5.22, stroke_opacity=0, fill_opacity=0,
        )
        zona_izq.next_to(linea, DOWN, buff=0.30)
        zona_izq.to_edge(LEFT, buff=0.65)

        subtitulo = txt("DFS recorre cada componente por separado", 25, SUB)
        ajustar(subtitulo, ancho=zona_izq.width - 0.24)
        subtitulo.next_to(linea, DOWN, buff=0.30)
        subtitulo.align_to(zona_izq, LEFT)

        # Las 3 tarjetas se ordenan DENTRO de la columna izquierda.
        # Esta separación asegura que no se conecten visualmente como si
        # fueran una única componente.
        dimensiones = [(2.23, 3.31), (2.79, 3.31), (1.78, 3.31)]
        cajas = VGroup(*[
            RoundedRectangle(
                width=w, height=h, corner_radius=0.17,
                stroke_color=BORDER, stroke_width=2,
                fill_color=PANEL, fill_opacity=0.91,
            ) for w, h in dimensiones
        ])
        cajas.arrange(RIGHT, aligned_edge=UP, buff=0.21)
        ajustar(cajas, ancho=zona_izq.width - 0.10)
        cajas.next_to(subtitulo, DOWN, buff=0.36)
        cajas.align_to(zona_izq, LEFT)
        for c in cajas:
            c.set_z_index(-2)

        # Títulos internos relativos a cada tarjeta (sin coordenadas globales).
        encabezados = VGroup()
        for i, caja in enumerate(cajas):
            nombre = ("COMPONENTE 1", "COMPONENTE 2", "AISLADO")[i]
            titulo = txt(nombre, 18, BLUE_ACCENT)
            ajustar(titulo, ancho=caja.width - 0.23)
            titulo.next_to(caja.get_top(), DOWN, buff=0.28)
            titulo.move_to([caja.get_center()[0], titulo.get_center()[1], 0])
            encabezados.add(titulo)
            dentro(titulo, caja, f"Título tarjeta {i+1}", padding=0.11)

        # Geometría de los nodos relativa a las tarjetas, no a ORIGIN.
        # Aristas, IDs y sus recorridos se cargan siempre desde el JSON.
        a, b, c = cajas
        p1 = a.get_top() + DOWN * 1.00
        p4 = b.get_top() + DOWN * 1.00
        p8 = c.get_center() + UP * 0.18
        pos = {
            1: p1,
            2: p1 + LEFT * 0.59 + DOWN * 0.90,
            3: p1 + RIGHT * 0.59 + DOWN * 0.90,
            4: p4,
            5: p4 + LEFT * 0.72 + DOWN * 0.76,
            6: p4 + RIGHT * 0.72 + DOWN * 0.76,
            7: p4 + RIGHT * 0.72 + DOWN * 1.42,
            8: p8,
        }
        posiciones = {v: (p[0], p[1]) for v, p in pos.items()}
        g = Grafico(datos, posiciones, radio=0.265)
        g.grupo.set_z_index(2)
        # Antes de animar, comprobar nodos, aristas y títulos de cada caja.
        for i, ids in enumerate(componentes):
            for v in ids:
                dentro(g.nodes[v], cajas[i], f"Nodo {v}", padding=0.10)
                separados(g.nodes[v], encabezados[i], f"Nodo {v} / título", 0.08)
        for ar in datos["aristas"]:
            componente = next(i for i, ids in enumerate(componentes)
                              if ar["u"] in ids)
            dentro(g.edges[ar["id"]], cajas[componente],
                   f"Arista {ar['u']}-{ar['v']}", padding=0.10)

        # Etiquetas del caso borde, aparecen SOLO tras los eventos C++.
        t8 = vertices[8]
        marca_in = txt(f"tin = {t8['tin']}", 18, YELLOW)
        marca_out = txt(f"tout = {t8['tout']}", 18, GREEN)
        marcas_aislado = VGroup(marca_in, marca_out).arrange(DOWN, buff=0.11)
        ajustar(marcas_aislado, ancho=c.width - 0.26)
        marcas_aislado.next_to(g.nodes[8], DOWN, buff=0.26)
        dentro(marcas_aislado, c, "Marcas del vértice aislado", padding=0.12)
        separados(marcas_aislado, g.nodes[8], "Nodo aislado / marcas", 0.08)

        # Banda explicativa bajo las tarjetas; nunca se cruza con nodos.
        banda = RoundedRectangle(
            width=cajas.width, height=0.70, corner_radius=0.13,
            fill_color="#172B43", fill_opacity=0.98,
            stroke_color=BORDER, stroke_width=1.6,
        )
        banda.next_to(cajas, DOWN, buff=0.32)
        banda.align_to(cajas, LEFT)
        aviso = txt("La búsqueda continúa desde otra raíz sin visitar.", 20, SUB)
        ajustar(aviso, ancho=banda.width - 0.40)
        aviso.move_to(banda)
        separados(cajas, banda, "tarjetas / banda", 0.18)

        # ---------------- Panel derecho: reloj y bosque ----------------
        panel_derecho = RoundedRectangle(
            width=4.67, height=4.76, corner_radius=0.20,
            stroke_color=BORDER, stroke_width=2,
            fill_color=PANEL, fill_opacity=0.98,
        )
        panel_derecho.next_to(subtitulo, DOWN, buff=0.36)
        panel_derecho.to_edge(RIGHT, buff=0.60)
        panel_derecho.set_z_index(-2)

        titulo_panel = txt("BOSQUE DFS", 26, BLUE_ACCENT)
        intro_panel = txt("Cada componente inicia un nuevo árbol", 17, SUB)
        reloj_label = txt("RELOJ DE EVENTOS", 17, MUTED)
        reloj = txt(f"00 / {numero_total:02d}", 48, YELLOW, mono=True)
        leyenda = VGroup(
            VGroup(Dot(radius=0.07, color=YELLOW), txt("tin = entrar", 16, SUB))
            .arrange(RIGHT, buff=0.10),
            VGroup(Dot(radius=0.07, color=GREEN), txt("tout = salir", 16, SUB))
            .arrange(RIGHT, buff=0.10),
        ).arrange(RIGHT, buff=0.24)
        estado_label = txt("EVENTO ACTUAL", 17, MUTED)

        # Un espacio RESERVADO de ancho constante para los 19 mensajes
        # dinámicos. Se escala y posiciona JUNTO CON el contenido del panel:
        # nunca usamos el ancho del último texto animado para el siguiente.
        marco_estado = Rectangle(
            width=panel_derecho.width - 0.78,
            height=0.44,
            stroke_opacity=0,
            fill_opacity=0,
        )
        estado = estado_ajustado("Esperando el primer vértice", panel_derecho)
        ajustar(estado, ancho=marco_estado.width - 0.18,
                alto=marco_estado.height - 0.10)
        estado.move_to(marco_estado)
        bloque_estado = VGroup(marco_estado, estado)
        resumen_label = txt("ÁRBOLES TERMINADOS", 17, BLUE_ACCENT)
        filas = VGroup(*[
            txt(
                f"Raíz {r}: [{vertices[r]['tin']}, {vertices[r]['tout']}]"
                f"  ·  {len(componentes[i])} vértices",
                18, TEXT,
            ) for i, r in enumerate(raices)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        # Disposición interna: bloques, no textos sueltos en coordenadas.
        contenido = VGroup(
            titulo_panel, intro_panel, reloj_label, reloj,
            leyenda, estado_label, bloque_estado, resumen_label, filas,
        )
        contenido.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        ajustar(contenido, ancho=panel_derecho.width - 0.62,
                alto=panel_derecho.height - 0.67)
        contenido.move_to(panel_derecho)
        contenido.set_z_index(3)
        dentro(contenido, panel_derecho, "Contenido del panel", padding=0.30)
        dentro(marco_estado, panel_derecho, "Zona fija del estado", padding=0.29)
        dentro(estado, marco_estado, "Estado inicial", padding=0.04)
        for previo, siguiente in zip(list(contenido), list(contenido)[1:]):
            separados(previo, siguiente, "Dos bloques de la tarjeta", 0.06)

        # Las filas ocupan un lugar reservado pero aún NO se agregan a la
        # escena; cada una aparecerá al terminar el árbol correspondiente.

        # ---------------- Validación global de zonas -------------------
        separados(header, subtitulo, "header / subtítulo", 0.12)
        separados(header, cajas, "header / tarjetas", 0.12)
        separados(subtitulo, cajas, "subtítulo / tarjetas", 0.12)
        separados(header, panel_derecho, "header / panel", 0.12)
        separados(subtitulo, panel_derecho, "subtítulo / panel", 0.12)
        separados(cajas, panel_derecho, "tarjetas / panel", 0.22)
        separados(banda, panel_derecho, "banda / panel", 0.22)
        for nombre, mobj in [("header", header), ("subtítulo", subtitulo),
                            ("tarjetas", cajas), ("banda", banda),
                            ("panel derecho", panel_derecho)]:
            dentro_pantalla(mobj, nombre)

        # ---------------- Animación: 42 segundos -----------------------
        def construir_estado(mensaje, color=TEXT):
            # El rectángulo transparente es nuestra ÚNICA referencia, incluso
            # después de una secuencia de Transform. Evita textos que se salen
            # a la derecha al crecer respecto al texto anterior.
            objetivo = txt(mensaje, 22, color)
            ajustar(objetivo, ancho=marco_estado.width - 0.16,
                    alto=marco_estado.height - 0.09)
            objetivo.move_to(marco_estado.get_center())
            dentro(objetivo, marco_estado, "Mensaje: " + mensaje, padding=0.035)
            dentro(objetivo, panel_derecho, "Mensaje en panel", padding=0.27)
            separados(objetivo, estado_label, "Mensaje / título de evento", 0.05)
            separados(objetivo, resumen_label, "Mensaje / resumen", 0.05)
            return objetivo

        def nuevo_estado(mensaje, color=TEXT):
            return Transform(estado, construir_estado(mensaje, color))

        # Posición y alto originales son constantes; la animación nunca debe
        # reducir sucesivamente las dimensiones de mensajes posteriores.
        aviso_centro = aviso.get_center().copy()
        aviso_alto = aviso.height

        def construir_aviso(mensaje, color=SUB):
            destino = txt(mensaje, 20, color)
            ajustar(destino, ancho=banda.width - 0.40, alto=aviso_alto)
            destino.move_to(aviso_centro)
            dentro(destino, banda, "Aviso: " + mensaje, padding=0.11)
            return destino

        def nuevo_aviso(mensaje, color=SUB):
            return Transform(aviso, construir_aviso(mensaje, color))

        def reloj_a(valor, color):
            destino = txt(f"{valor:02d} / {numero_total:02d}", 48, color, mono=True)
            destino.scale_to_fit_height(reloj.height)
            destino.move_to(reloj)
            return Transform(reloj, destino)

        # PREFLIGHT: incluso los textos que aparecerán al FINAL se comprueban
        # ANTES de gastar tiempo de render. Si uno no cabe, se detecta aquí.
        mensajes_estado = [
            (f"Nueva raíz: vértice {r}", BLUE_ACCENT) for r in raices
        ]
        for evento in eventos:
            if evento["tipo"] in ("entrar", "salir"):
                es_entrada = evento["tipo"] == "entrar"
                accion = "ENTRADA" if es_entrada else "SALIDA"
                atributo = "tin" if es_entrada else "tout"
                color = YELLOW if es_entrada else GREEN
                mensajes_estado.append((
                    f"{accion} · nodo {evento['u']} · {atributo}={evento['t']}", color
                ))
        mensajes_estado.append(("¡Tres árboles DFS construidos!", GREEN))
        for mensaje, color in mensajes_estado:
            construir_estado(mensaje, color)
        for mensaje, color in [
            ("El vértice 8 no tiene conexiones.", YELLOW),
            ("DFS terminó el primer árbol; aún quedan nodos.", SUB),
            ("Terminó el segundo árbol; falta un vértice.", SUB),
            ("Un vértice aislado también recibe tin y tout.", GREEN),
        ]:
            construir_aviso(mensaje, color)

        self.animar(FadeIn(header), segundos=1.0)
        self.animar(FadeIn(subtitulo), segundos=0.8)
        self.animar(LaggedStart(*[FadeIn(caja) for caja in cajas], lag_ratio=0.22),
                    segundos=1.4)
        self.animar(FadeIn(encabezados), FadeIn(g.grupo), segundos=1.4)
        contenido_sin_filas = VGroup(
            titulo_panel, intro_panel, reloj_label, reloj,
            leyenda, estado_label, bloque_estado, resumen_label,
        )
        self.animar(FadeIn(banda), FadeIn(aviso), FadeIn(panel_derecho),
                    FadeIn(contenido_sin_filas), segundos=1.4)
        self.pausa(1.0)

        # Este bucle es el motor de las animaciones: eventos reales, mismo orden.
        raiz_activa = None
        indice_activo = None
        ultimo_t = 0
        for e in eventos:
            tipo, u = e["tipo"], e["u"]
            if tipo == "nuevo_arbol":
                raiz_activa = u
                indice_activo = raices.index(u)
                anims = [
                    cajas[indice_activo].animate.set_stroke(
                        color=BLUE_ACCENT, width=3.7),
                    nuevo_estado(f"Nueva raíz: vértice {u}", BLUE_ACCENT),
                ]
                if u == 8:
                    anims.append(nuevo_aviso(
                        "El vértice 8 no tiene conexiones.", YELLOW))
                self.animar(*anims, segundos=0.70)
                if u == 1:
                    self.pausa(0.85)
                elif u == 4:
                    self.pausa(0.95)
                else:
                    self.pausa(1.65)

            elif tipo == "mirar":
                clase = e["clase"]
                arista = g.edges[e["arista"]]
                if clase == "arbol":
                    brillo = arista.copy().set_stroke(
                        color=BLUE_ACCENT, width=9)
                    self.animar(
                        ShowPassingFlash(brillo, time_width=0.75),
                        segundos=0.38,
                    )
                elif clase == "retroceso":
                    self.animar(arista.animate.set_stroke(
                        color=RED, width=5.5), segundos=0.38)
                # 'padre' y 'retroceso_vista' se procesan, pero no generan
                # desplazamiento ni timestamp, por lo que no los exageramos.

            elif tipo in ("entrar", "salir"):
                t = e["t"]
                assert t == ultimo_t + 1
                ultimo_t = t
                entrada = tipo == "entrar"
                color = YELLOW if entrada else GREEN
                sufijo = "tin" if entrada else "tout"
                accion = "ENTRADA" if entrada else "SALIDA"
                anims = [
                    reloj_a(t, color),
                    nuevo_estado(f"{accion} · nodo {u} · {sufijo}={t}", color),
                    g.nodes[u][0].animate.set_fill(color, opacity=0.96)
                                 .set_stroke(color, width=3),
                ]
                if u == 8:
                    anims.append(FadeIn(marca_in if entrada else marca_out))
                self.animar(*anims, segundos=0.72 if u != 8 else 0.82)
                if entrada and u == 8:
                    self.pausa(1.20)

                # El bosque se actualiza al salir de la raíz de cada árbol,
                # no antes de haber terminado su componente.
                if not entrada and u == raiz_activa:
                    self.animar(
                        cajas[indice_activo].animate.set_stroke(
                            color=GREEN, width=2.8),
                        FadeIn(filas[indice_activo]),
                        segundos=0.58,
                    )
                    if u == 1:
                        self.animar(nuevo_aviso(
                            "DFS terminó el primer árbol; aún quedan nodos.",
                            SUB), segundos=0.48)
                        self.pausa(1.85)
                    elif u == 4:
                        self.animar(nuevo_aviso(
                            "Terminó el segundo árbol; falta un vértice.",
                            SUB), segundos=0.48)
                        self.pausa(1.65)
                    else:
                        self.pausa(2.40)

        assert ultimo_t == numero_total
        assert len(componentes) == len(raices) == 3

        self.animar(
            nuevo_estado("¡Tres árboles DFS construidos!", GREEN),
            nuevo_aviso("Un vértice aislado también recibe tin y tout.", GREEN),
            segundos=1.0,
        )
        self.animar(
            Circumscribe(cajas[2], color=YELLOW, buff=0.11),
            segundos=1.30,
        )
        self.pausa(2.6)
        self.completar()  # Garantiza exactamente 42 segundos o revela un exceso.
