# CS2023-DFS-Timestamps

**DFS con timestamps (`tin` / `tout`)** implementado desde cero en **C++** (DFS iterativo con pila explícita), junto con un **video animado en Manim** cuyas escenas se generan a partir de la ejecución real del código.

Proyecto Final 2 — CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2) · Grupo 8.

**Video (4:52):** https://youtu.be/yxcpK0j2PvE

## ¿Qué hace?

Un DFS con un reloj anota, para cada vértice, el tiempo de entrada `tin` y de salida `tout`. Los intervalos `[tin, tout]` nunca se cruzan: o son disjuntos o uno contiene al otro. Con un solo recorrido en **O(n + m)** se responde en **O(1)**:

- `esAncestro(u, v)`: `tin[u] ≤ tin[v] && tout[v] ≤ tout[u]`
- `tamanoSubarbol(u)`: `(tout[u] − tin[u] + 1) / 2`

Además clasifica aristas (árbol, retroceso, avance, cruce), recupera ciclos, calcula el orden topológico y funciona en grafos dirigidos, no dirigidos y desconectados.

El programa registra cada paso (`nuevo_arbol`, `entrar`, `mirar`, `salir`) en archivos **JSON**. Las animaciones leen esos archivos, así que lo que se ve en pantalla proviene de la ejecución real del código.

## Estructura del repositorio

```
├── cpp/dfs_timestamps.cpp       # Implementación + exportación de eventos
├── datos/                       # JSON generados por el C++
├── escenas/                     # visual.py + 7 escenas de Manim (01–07)
├── scripts/                     # generar_datos.ps1 (Windows) / generar_datos.sh (macOS, Linux)
├── requirements.txt             # manim==0.21.0
├── .gitignore
└── README.md
```

## Requisitos

g++ con soporte C++17, Python 3.10+ (probado con 3.14), FFmpeg en el PATH y Manim Community v0.21.0 (no requiere LaTeX).

```bash
python3 -m venv venv
source venv/bin/activate