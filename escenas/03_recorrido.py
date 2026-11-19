
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manim import *
from visual import (
    SceneWithTiming, Grafico, cargar, vertex, cabecera, txt, POS_CLASE,
    BG, PANEL, BORDER, TEXT, SUB, MUTED, EDGE,
    BLUE_ACCENT, YELLOW, GREEN, RED, PURPLE,
)

# Una misma configuración se usa en la escena y en las marcas del guion.
# Cada clase de evento tiene [tiempo de animación, pausa para explicar].
DURACION_EVENTO = {
    "nuevo_arbol": (0.90, 1.00),
    "entrar": (1.55, 2.10),
    "salir": (1.45, 2.10),
    "arbol": (1.00, 1.35),
    "retroceso": (1.25, 3.10),
    "padre": (0.40, 0.12),
    "retroceso_vista": (0.40, 0.12),
}
PAUSAS_CLAVE = {
    # índice real del evento JSON -> pausa didáctica adicional
    1: 1.00,   # tin[1] = 1, primera marca
    9: 1.00,   # tin[5] = 4, profundidad máxima primera rama
    12: 1.50,  # tout[5] = 5, primer retroceso
    15: 1.50,  # tout[2] = 7, intervalo cerrado
    17: 0.80,  # tin[4] = 8, segunda rama
    30: 1.50,  # tout[1] = 14, marca final
}


def ajustar_maximo(mob, ancho=None, alto=None):

    if ancho is not None and mob.width > ancho:
        mob.scale_to_fit_width(ancho)
    if alto is not None and mob.height > alto:
        mob.scale_to_fit_height(alto)
    return mob


def comprobar_separacion(a, b, nombre_a, nombre_b, margen=0.12):

    separados_en_x = (a.get_right()[0] + margen <= b.get_left()[0]
                       or b.get_right()[0] + margen <= a.get_left()[0])
    separados_en_y = (a.get_top()[1] + margen <= b.get_bottom()[1]
                       or b.get_top()[1] + margen <= a.get_bottom()[1])
    if not (separados_en_x or separados_en_y):
        raise ValueError(f"Colisión entre {nombre_a} y {nombre_b}.")


def comprobar_dentro(contenido, caja, nombre, margen=0.24):
    if not (
        contenido.get_left()[0] >= caja.get_left()[0] + margen - 0.008
        and contenido.get_right()[0] <= caja.get_right()[0] - margen + 0.008
        and contenido.get_bottom()[1] >= caja.get_bottom()[1] + margen - 0.008
        and contenido.get_top()[1] <= caja.get_top()[1] - margen + 0.008
    ):
        raise ValueError(f"{nombre} se sale de su área de seguridad.")


def comprobar_pantalla(mob, nombre, margen=0.16):
    ancho_mitad, alto_mitad = config.frame_width / 2, config.frame_height / 2
    if not (
        mob.get_left()[0] >= -ancho_mitad + margen
        and mob.get_right()[0] <= ancho_mitad - margen
        and mob.get_top()[1] <= alto_mitad - margen
        and mob.get_bottom()[1] >= -alto_mitad + margen
    ):
        raise ValueError(f"{nombre} queda fuera de pantalla.")


def minitexto(cadena, color=SUB, tamaño=18):
    return txt(str(cadena), tamaño, color, mono=True)


def celda_tabla(texto, ancho, alto=0.34, color=TEXT, fuente=19):

    ancla = Rectangle(width=ancho, height=alto, stroke_opacity=0, fill_opacity=0)
    valor = minitexto(texto, color, fuente)
    ajustar_maximo(valor, ancho=ancho - 0.10, alto=alto - 0.055)
    valor.move_to(ancla.get_center())
    return VGroup(ancla, valor), valor


def ficha_pila(n):
    caja = RoundedRectangle(
        width=0.52, height=0.38, corner_radius=0.095,
        stroke_color=BLUE_ACCENT, stroke_width=1.8,
        fill_color="#233956", fill_opacity=1,
    )
    numero = minitexto(n, TEXT, 19).move_to(caja)
    return VGroup(caja, numero)


class S03Recorrido(SceneWithTiming):
    OBJETIVO = 112.0

    def construct(self):
        # ==============================================================
        # 1. Validación de la traza real C++ (NO introducir tiempos aquí).
        # ==============================================================
        datos = cargar("grafo_clase.json")
        eventos = datos["eventos"]
        n = datos["n"]
        if len(eventos) != 31 or n != 7:
            raise ValueError("El JSON no coincide con el ejemplo de 7 nodos y 31 eventos")

        marcas = [e for e in eventos if e["tipo"] in ("entrar", "salir")]
        if [e["t"] for e in marcas] != list(range(1, 2 * n + 1)):
            raise ValueError("El reloj C++ debe generar marcas consecutivas 1..2n")
        if any(e["paso"] != i for i, e in enumerate(eventos)):
            raise ValueError("Los eventos deben conservar el orden C++")

        # ==============================================================
        # 2. Layout: encabezado + dos columnas totalmente independientes.
        # ==============================================================
        encabezado = cabecera(
            "DFS en acción: de las visitas a los timestamps",
            "03 · Recorrido real",
        )
        header_line = encabezado[-1]

        zona_izq = Rectangle(
            width=config.frame_width * 0.50,
            height=config.frame_height * 0.68,
            stroke_opacity=0, fill_opacity=0,
        )
        zona_izq.next_to(header_line, DOWN, buff=0.27)
        zona_izq.to_edge(LEFT, buff=0.66)

        subtitulo = txt("El reloj cuenta eventos, no segundos reales", 24, SUB)
        ajustar_maximo(subtitulo, ancho=zona_izq.width - 0.20)
        subtitulo.next_to(header_line, DOWN, buff=0.30)
        subtitulo.align_to(zona_izq, LEFT)

        tarjeta = RoundedRectangle(
            width=5.00, height=5.26, corner_radius=0.22,
            stroke_color=BORDER, stroke_width=2,
            fill_color=PANEL, fill_opacity=0.985,
        )
        # Bajo la altura del subtítulo, con margen derecho > 0.5.
        tarjeta.next_to(subtitulo, DOWN, buff=0.29)
        tarjeta.to_edge(RIGHT, buff=0.66)
        tarjeta.set_z_index(1)

        # ==============================================================
        # 3. Grafo (topología real); las mini-etiquetas se agregan ANTES
        #    de escalar para que todas las piezas se muevan juntas.
        # ==============================================================
        g = Grafico(datos, POS_CLASE, radio=0.33)
        etiquetas = {}
        fichas_tiempo = VGroup()

        for u in range(1, n + 1):
            fondo_tiempo = RoundedRectangle(
                width=1.10, height=0.34, corner_radius=0.085,
                stroke_color=BORDER, stroke_width=1.2,
                fill_color=BG, fill_opacity=0.95,
            )
            texto_tiempo = minitexto("-- / --", MUTED, 16)
            ajustar_maximo(texto_tiempo, ancho=fondo_tiempo.width - 0.10)
            texto_tiempo.move_to(fondo_tiempo)
            ficha = VGroup(fondo_tiempo, texto_tiempo)
            ficha.next_to(g.nodes[u][0], DOWN, buff=0.12)
            etiquetas[u] = texto_tiempo
            fichas_tiempo.add(ficha)

        diagrama = VGroup(g.grupo, fichas_tiempo)
        ajustar_maximo(
            diagrama,
            ancho=min(config.frame_width * 0.50, zona_izq.width - 0.22),
            alto=config.frame_height * 0.52,
        )
        diagrama.next_to(subtitulo, DOWN, buff=0.38)
        diagrama.align_to(zona_izq, LEFT)

        # Área de mensaje de 2 líneas (debajo de TODO el diagrama).
        caja_mensaje = RoundedRectangle(
            width=zona_izq.width - 0.12, height=0.76,
            corner_radius=0.16, stroke_color=BORDER,
            stroke_width=1.6, fill_color=PANEL, fill_opacity=0.88,
        )
        caja_mensaje.next_to(diagrama, DOWN, buff=0.25)
        caja_mensaje.align_to(zona_izq, LEFT)

        texto_accion = txt("¿Qué está haciendo DFS?", 21, BLUE_ACCENT)
        texto_explicacion = txt("Observa las entradas, salidas y retrocesos.", 17, SUB)
        estado_visual = VGroup(texto_accion, texto_explicacion).arrange(
            DOWN, aligned_edge=LEFT, buff=0.065,
        )
        ajustar_maximo(
            estado_visual,
            ancho=caja_mensaje.width - 0.40,
            alto=caja_mensaje.height - 0.20,
        )
        estado_visual.move_to(caja_mensaje)

        # ==============================================================
        # 4. Tarjeta derecha: reloj de 14 marcas, tabla, pila visible.
        #    Contenido agrupado y autoajustable al interior del panel.
        # ==============================================================
        limite_tabla = tarjeta.width - 0.66

        rotulo_reloj = txt("RELOJ", 20, BLUE_ACCENT)
        numero_reloj = minitexto("00", YELLOW, 43)  # 2 cifras: evita saltos de ancho
        leyenda_reloj = txt("cada entrada o salida = 1 marca", 15, SUB)
        bloque_reloj = VGroup(rotulo_reloj, numero_reloj, leyenda_reloj)
        bloque_reloj.arrange(RIGHT, buff=0.22)
        ajustar_maximo(bloque_reloj, ancho=limite_tabla)

        puntos_reloj = VGroup()
        for _ in range(2 * n):
            casilla = RoundedRectangle(
                width=0.235, height=0.155, corner_radius=0.04,
                stroke_color=BORDER, stroke_width=1,
                fill_color="#2D405A", fill_opacity=1,
            )
            puntos_reloj.add(casilla)
        puntos_reloj.arrange(RIGHT, buff=0.062)
        ajustar_maximo(puntos_reloj, ancho=limite_tabla)

        separador1 = Line(LEFT * (limite_tabla / 2), RIGHT * (limite_tabla / 2),
                         stroke_width=1, color=BORDER)
        separador2 = separador1.copy()

        ancho_columnas = (1.47, 1.15, 1.15)
        espacio_columnas = 0.11
        ancho_fila = sum(ancho_columnas) + 2 * espacio_columnas

        def fila_campos(u, t_in, t_out, cabecera_fila=False):
            color_fila = MUTED if cabecera_fila else TEXT
            elementos = []
            referencias = []
            for valor, ancho, color in (
                (u, ancho_columnas[0], color_fila),
                (t_in, ancho_columnas[1], YELLOW if not cabecera_fila else SUB),
                (t_out, ancho_columnas[2], GREEN if not cabecera_fila else SUB),
            ):
                celda, texto_celda = celda_tabla(
                    valor, ancho, alto=0.337,
                    color=color, fuente=17 if cabecera_fila else 19,
                )
                elementos.append(celda)
                # Se guarda también el ancla (celda[0]): su tamaño no cambia con
                # los Transform y sirve de referencia fija para los dígitos.
                referencias.append((celda[0], texto_celda))
            contenido_fila = VGroup(*elementos).arrange(RIGHT, buff=espacio_columnas)
            fondo_fila = RoundedRectangle(
                width=ancho_fila, height=0.355,
                corner_radius=0.075, stroke_width=0,
                fill_color="#233653" if cabecera_fila else BG,
                fill_opacity=0.63 if cabecera_fila else 0.20,
            )
            contenido_fila.move_to(fondo_fila)
            fila = VGroup(fondo_fila, contenido_fila)
            return fila, fondo_fila, referencias

        encabezado_tabla, _, _ = fila_campos("NODO", "tin", "tout", True)
        filas = {}
        fondofilas = {}
        casillas_tin = {}
        casillas_tout = {}
        tabla_filas = [encabezado_tabla]
        for u in range(1, n + 1):
            fila, fondo, refs = fila_campos(str(u), "--", "--")
            filas[u] = fila
            fondofilas[u] = fondo
            casillas_tin[u] = refs[1]    # (ancla, texto)
            casillas_tout[u] = refs[2]
            tabla_filas.append(fila)

        tabla = VGroup(*tabla_filas).arrange(DOWN, buff=0.049)

        rotulo_pila = txt("PILA ACTIVA  ·  cima a la derecha", 16, BLUE_ACCENT)
        hueco_pila = RoundedRectangle(
            width=ancho_fila, height=0.45, corner_radius=0.09,
            stroke_color=BORDER, stroke_width=1,
            fill_color=BG, fill_opacity=0.85,
        )

        contenido_tarjeta = VGroup(
            bloque_reloj, puntos_reloj, separador1, tabla,
            separador2, rotulo_pila, hueco_pila,
        )
        contenido_tarjeta.arrange(DOWN, aligned_edge=LEFT, buff=0.085)
        ajustar_maximo(
            contenido_tarjeta,
            ancho=tarjeta.width - 0.58,
            alto=tarjeta.height - 0.56,
        )
        contenido_tarjeta.move_to(tarjeta)
        contenido_tarjeta.set_z_index(2)

        pila_actual = txt("vacía", 17, SUB).move_to(hueco_pila)
        pila_actual.set_z_index(3)

        # ==============================================================
        # 5. Verificaciones de colisión — antes del primer fotograma.
        # ==============================================================
        comprobar_separacion(encabezado, subtitulo, "encabezado", "subtítulo")
        comprobar_separacion(subtitulo, diagrama, "subtítulo", "diagrama")
        comprobar_separacion(subtitulo, tarjeta, "subtítulo", "tarjeta")
        comprobar_separacion(diagrama, caja_mensaje, "diagrama", "mensaje", 0.17)
        comprobar_separacion(diagrama, tarjeta, "diagrama", "tarjeta", 0.32)
        comprobar_separacion(caja_mensaje, tarjeta, "mensaje", "tarjeta", 0.26)
        comprobar_dentro(estado_visual, caja_mensaje, "Texto de explicación", 0.09)
        comprobar_dentro(contenido_tarjeta, tarjeta, "Contenido de tarjeta", 0.26)
        for mob, nombre in (
            (encabezado, "encabezado"), (subtitulo, "subtítulo"),
            (diagrama, "diagrama"), (caja_mensaje, "mensaje"),
            (tarjeta, "tarjeta"),
        ):
            comprobar_pantalla(mob, nombre, 0.17)

        # ==============================================================
        # 6. Herramientas para actualizar elementos solo con eventos C++.
        # ==============================================================
        estado = {u: {"tin": None, "tout": None} for u in range(1, n + 1)}
        pila_anterior = []
        nodo_resaltado = None

        def texto_actual(nodo):
            tin = estado[nodo]["tin"]
            tout = estado[nodo]["tout"]
            return f"{tin if tin is not None else '--'} / {tout if tout is not None else '--'}"

        def nuevo_texto_centrado(anterior, texto, color, tamaño=20, mono=False):
            nuevo = txt(str(texto), tamaño, color, mono=mono)
            # El texto nuevo debe caber en la REGIÓN del existente.
            max_ancho = (
                caja_mensaje.width - 0.43
                if anterior is texto_accion or anterior is texto_explicacion
                else None
            )
            ajustar_maximo(nuevo, ancho=max_ancho)
            if anterior is numero_reloj:
                ajustar_maximo(nuevo, alto=numero_reloj.height)
            nuevo.move_to(anterior)
            if max_ancho is not None:
                # Centrar en la caja, no en el texto anterior (que estaba
                # alineado a la izquierda): evita que un texto largo se salga.
                nuevo.set_x(caja_mensaje.get_x())
            return nuevo

        def mensajes_evento(e):
            tipo, u = e["tipo"], e["u"]
            if tipo == "nuevo_arbol":
                return (f"INICIAMOS EN EL VÉRTICE {u}",
                        "La raíz todavía no tiene marcas de tiempo.", BLUE_ACCENT)
            if tipo == "entrar":
                return (f"ENTRAR EN {u}  ·  tin[{u}] = {e['t']}",
                        "Descubrimos un vértice; guardamos su entrada.", YELLOW)
            if tipo == "salir":
                return (f"SALIR DE {u}  ·  tout[{u}] = {e['t']}",
                        "Ya no hay vecinos nuevos: cerramos el intervalo.", GREEN)
            v, clase = e["v"], e["clase"]
            if clase == "arbol":
                return (f"EXPLORAR {u} → {v}",
                        "Es un vecino nuevo: seguimos más profundo.", BLUE_ACCENT)
            if clase == "retroceso":
                return (f"RETROCESO {u} → {v}  ·  CICLO",
                        "Volvemos a un ancestro activo: no lo visitamos otra vez.", RED)
            if clase == "padre":
                return (f"ARISTA {u} → {v}  ·  PADRE",
                        "Es la arista por la que llegamos: la ignoramos.", MUTED)
            if clase == "retroceso_vista":
                return (f"ARISTA {u} — {v}  ·  YA VISTA",
                        "El mismo enlace fue revisado desde el otro extremo.", MUTED)
            raise ValueError(f"Clase de arista inesperada: {clase}")

        def nuevo_contenido_pila(pila):
            if not pila:
                obj = txt("vacía", 17, SUB)
            else:
                obj = VGroup(*(ficha_pila(u) for u in pila)).arrange(RIGHT, buff=0.12)
            ajustar_maximo(obj, ancho=hueco_pila.width - 0.20,
                           alto=hueco_pila.height - 0.06)
            obj.move_to(hueco_pila)
            obj.set_z_index(3)
            return obj

        # Altura de referencia para los tiempos: el número "1" de la columna
        # NODO (filas[1][1][0][1]), ya escalado junto con la tarjeta. Antes se
        # usaba la altura de "--", casi nula, y los números quedaban como puntos.
        alto_digitos = filas[1][1][0][1].height

        def nuevo_valor_tabla(ancla, valor, color):
            nuevo = minitexto(valor, color, 19)
            nuevo.scale_to_fit_height(alto_digitos)
            ajustar_maximo(nuevo, ancho=ancla.width - 0.08, alto=ancla.height * 0.85)
            nuevo.move_to(ancla.get_center())
            return nuevo

        # ==============================================================
        # 7. INTRODUCCIÓN: zonas aparecen ordenadamente (10 segundos).
        # ==============================================================
        self.animar(FadeIn(encabezado), segundos=1.00)
        self.animar(FadeIn(subtitulo), segundos=0.80)
        self.pausa(1.30)
        self.animar(Create(g.grupo), FadeIn(fichas_tiempo), segundos=2.10)
        self.animar(FadeIn(tarjeta), FadeIn(contenido_tarjeta),
                    FadeIn(pila_actual), segundos=1.60)
        self.animar(FadeIn(caja_mensaje), FadeIn(estado_visual), segundos=0.80)
        self.pausa(2.40)   # TOTAL INTRO = 10.0 s

        # ==============================================================
        # 8. Evento a evento: ningún paso ni número está animado a mano.
        # ==============================================================
        for e in eventos:
            tipo, u = e["tipo"], e["u"]
            categoria = tipo if tipo != "mirar" else e["clase"]
            duracion, pausa = DURACION_EVENTO[categoria]
            titulo_nuevo, detalle_nuevo, color = mensajes_evento(e)

            anims = [
                Transform(
                    texto_accion,
                    nuevo_texto_centrado(texto_accion, titulo_nuevo, color, 21),
                ),
                Transform(
                    texto_explicacion,
                    nuevo_texto_centrado(texto_explicacion, detalle_nuevo, SUB, 17),
                ),
            ]

            if e["pila"] != pila_anterior:
                proxima_pila = nuevo_contenido_pila(e["pila"])
                anims += [FadeOut(pila_actual), FadeIn(proxima_pila)]
            else:
                proxima_pila = None

            marcador = None
            if tipo == "mirar":
                clase = e["clase"]
                if clase in ("arbol", "retroceso"):
                    tono = BLUE_ACCENT if clase == "arbol" else RED
                    # El punto recorre la arista real que marca el evento.
                    camino = Line(g.nodes[u].get_center(),
                                  g.nodes[e["v"]].get_center())
                    marcador = Dot(point=g.nodes[u].get_center(),
                                   radius=0.105, color=tono)
                    marcador.set_z_index(6)
                    self.add(marcador)
                    anims.extend([
                        MoveAlongPath(marcador, camino),
                        g.colorear_arista(e["arista"], tono, grosor=7),
                    ])
                # Padre y aristas ya vistas: lectura rápida sin recolorearlas.

            elif tipo in ("entrar", "salir"):
                t = e["t"]
                campo = "tin" if tipo == "entrar" else "tout"
                estado[u][campo] = t
                tono = YELLOW if tipo == "entrar" else GREEN
                ancla, celda = casillas_tin[u] if tipo == "entrar" else casillas_tout[u]

                anims.extend([
                    g.colorear_nodo(u, tono),
                    Transform(
                        numero_reloj,
                        nuevo_texto_centrado(numero_reloj, f"{t:02d}", tono, 43, True),
                    ),
                    puntos_reloj[t - 1].animate.set_fill(tono, opacity=1).set_stroke(tono, width=1.3),
                    Transform(celda, nuevo_valor_tabla(ancla, t, tono)),
                    Transform(
                        etiquetas[u],
                        nuevo_texto_centrado(
                            etiquetas[u], texto_actual(u),
                            tono if tipo == "salir" else YELLOW,
                            16, True,
                        ),
                    ),
                ])
                if nodo_resaltado is not None and nodo_resaltado != u:
                    anims.append(fondofilas[nodo_resaltado].animate.set_fill(
                        BG, opacity=0.20,
                    ))
                anims.append(fondofilas[u].animate.set_fill(tono, opacity=0.24))
                nodo_resaltado = u

            self.animar(*anims, segundos=duracion)
            if marcador is not None:
                self.remove(marcador)
            if proxima_pila is not None:
                pila_actual = proxima_pila
                pila_anterior = list(e["pila"])

            self.pausa(pausa)
            self.pausa(PAUSAS_CLAVE.get(e["paso"], 0.0))

        # ==============================================================
        # 9. Cierre: resaltar por qué los intervalos son útiles.
        # ==============================================================
        for v in datos["vertices"]:
            u = v["id"]
            if estado[u]["tin"] != v["tin"] or estado[u]["tout"] != v["tout"]:
                raise ValueError(f"Inconsistencia entre animación y DFS para nodo {u}")

        vertice_2, vertice_5 = vertex(datos, 2), vertex(datos, 5)
        cierre_titulo = nuevo_texto_centrado(
            texto_accion, "CADA NODO TIENE DOS MARCAS", GREEN, 21,
        )
        cierre_detalle = nuevo_texto_centrado(
            texto_explicacion,
            f"{n} entradas + {n} salidas = {2*n} marcas consecutivas.",
            SUB, 17,
        )
        self.animar(
            Transform(texto_accion, cierre_titulo),
            Transform(texto_explicacion, cierre_detalle),
            segundos=1.50,
        )
        self.pausa(3.00)

        anidado_titulo = nuevo_texto_centrado(
            texto_accion, "LOS INTERVALOS SE PUEDEN COMPARAR", PURPLE, 21,
        )
        anidado_detalle = nuevo_texto_centrado(
            texto_explicacion,
            f"2 [{vertice_2['tin']}, {vertice_2['tout']}] contiene "
            f"a 5 [{vertice_5['tin']}, {vertice_5['tout']}].",
            TEXT, 17,
        )
        self.animar(
            Transform(texto_accion, anidado_titulo),
            Transform(texto_explicacion, anidado_detalle),
            Circumscribe(g.nodes[2][0], color=YELLOW),
            Circumscribe(g.nodes[5][0], color=GREEN),
            Circumscribe(filas[2], color=YELLOW),
            Circumscribe(filas[5], color=GREEN),
            segundos=2.25,
        )
        self.pausa(5.25)
        self.completar()  # Exactamente 112 segundos, sin acelerar los eventos.
