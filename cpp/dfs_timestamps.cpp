// =====================================================================
//  DFS con timestamps (tin / tout) — CS2023 Proyecto 2
//  Basado en la versión iterativa del grupo. Vértices 1..n.
//
//  Extensiones:
//   1. Registro de eventos (ENTRAR / MIRAR / SALIR) exportado a JSON
//      para que la animación en Manim se genere desde la ejecución real.
//   2. Clasificación de aristas:
//        no dirigido -> arbol, retroceso
//        dirigido    -> arbol, retroceso, avance, cruce
//   3. Modo dirigido / no dirigido.
//   4. Cuatro grafos de demostración (clase, desconectado, dirigido, carpetas).
//
//  Compilar:  g++ -std=c++17 -O2 -Wall dfs_timestamps.cpp -o dfs_timestamps
//  Ejecutar:  ./dfs_timestamps [carpeta_salida]      (por defecto: .)
//  Genera:    grafo_clase.json, grafo_desconectado.json, grafo_dirigido.json, grafo_carpetas.json
// =====================================================================
#include <algorithm>
#include <cassert>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// ---------------------------------------------------------------------
// Grafo: lista de adyacencia. Cada entrada guarda (vecino, id de arista)
// para que la animación sepa exactamente qué arista colorear.
// ---------------------------------------------------------------------
struct Grafo {
    int n = 0;
    bool dirigido = false;
    vector<pair<int,int>> aristas;            // aristas[id] = {u, v}
    vector<vector<pair<int,int>>> adj;         // adj[u] = {(v, id), ...}

    Grafo(int n_, bool dir) : n(n_), dirigido(dir), adj(n_ + 1) {}

    void agregarArista(int u, int v) {
        int id = (int)aristas.size();
        aristas.push_back({u, v});
        adj[u].push_back({v, id});
        if (!dirigido) adj[v].push_back({u, id});
    }
};

// ---------------------------------------------------------------------
// Eventos del recorrido (lo que Manim va a animar, en orden)
// ---------------------------------------------------------------------
enum class TipoEvento { NUEVO_ARBOL, ENTRAR, MIRAR, SALIR };

struct Evento {
    TipoEvento tipo;
    int u = -1;            // vértice actual
    int v = -1;            // vecino mirado (solo MIRAR)
    int arista = -1;       // id de arista (solo MIRAR)
    int t = -1;            // valor del reloj anotado (ENTRAR / SALIR)
    string clase;          // clasificación de la arista (solo MIRAR)
    vector<int> pila;      // contenido de la pila DESPUÉS del evento
};

// ---------------------------------------------------------------------
// Resultado del DFS
// ---------------------------------------------------------------------
struct DFS {
    vector<int> tin, tout, padre;
    vector<string> claseArista;     // claseArista[id]
    vector<Evento> eventos;
    vector<int> raices;             // una por árbol del bosque
    vector<vector<int>> ciclos;     // uno por arista de retroceso
    vector<int> ordenSalida;        // vértices en orden de tout creciente
};

// Recupera el ciclo que cierra la arista de retroceso u -> v
// (v es ancestro de u): v, ..., u subiendo por padre.
static vector<int> recuperarCiclo(int u, int v, const vector<int>& padre) {
    vector<int> c;
    for (int x = u; x != v; x = padre[x]) c.push_back(x);
    c.push_back(v);
    reverse(c.begin(), c.end());
    return c;
}

// O(n + m). Misma lógica que la versión del grupo: sig[u] es el próximo
// vecino por mirar (equivale al par (vértice, índice) de DFS-Iterativo).
DFS recorrerDFS(const Grafo& g) {
    const int n = g.n;
    DFS d;
    d.tin.assign(n + 1, 0);                    // 0 = no visitado
    d.tout.assign(n + 1, 0);                   // 0 = todavía en la pila
    d.padre.assign(n + 1, -1);
    d.claseArista.assign(g.aristas.size(), "");

    vector<int> aristaPadre(n + 1, -1);        // id de la arista padre[u]-u
    vector<int> sig(n + 1, 0);
    vector<int> pila;
    int reloj = 1;

    auto registrar = [&](TipoEvento tipo, int u, int v, int id, int t,
                         const string& clase) {
        Evento evento;
        evento.tipo = tipo;
        evento.u = u;
        evento.v = v;
        evento.arista = id;
        evento.t = t;
        evento.clase = clase;
        evento.pila = pila;
        d.eventos.push_back(evento);
    };

    for (int raiz = 1; raiz <= n; ++raiz) {
        if (d.tin[raiz] != 0) continue;
        d.raices.push_back(raiz);
        registrar(TipoEvento::NUEVO_ARBOL, raiz, -1, -1, -1, "");

        d.tin[raiz] = reloj++;
        pila.push_back(raiz);
        registrar(TipoEvento::ENTRAR, raiz, -1, -1, d.tin[raiz], "");

        while (!pila.empty()) {
            int u = pila.back();
            if (sig[u] < (int)g.adj[u].size()) {
                const pair<int,int>& vecino = g.adj[u][sig[u]++];
                int v = vecino.first;
                int id = vecino.second;
                string clase;

                if (d.tin[v] == 0) {
                    clase = "arbol";                       // v nuevo: entro
                } else if (!g.dirigido) {
                    if (id == aristaPadre[u])
                        clase = "padre";                   // misma arista de subida: se ignora
                    else if (d.tout[v] == 0)
                        clase = "retroceso";               // v es ancestro (sigue en la pila)
                    else
                        clase = "retroceso_vista";         // la misma arista de retroceso, vista desde el ancestro
                } else {
                    if (d.tout[v] == 0)
                        clase = "retroceso";               // v en la pila: cierra un ciclo
                    else if (d.tin[u] < d.tin[v])
                        clase = "avance";                  // v descendiente ya terminado
                    else
                        clase = "cruce";                   // v en otra rama u otro árbol
                }

                if (d.claseArista[id].empty() && clase != "retroceso_vista")
                    d.claseArista[id] = clase;
                if (clase == "retroceso")
                    d.ciclos.push_back(recuperarCiclo(u, v, d.padre));

                registrar(TipoEvento::MIRAR, u, v, id, -1, clase);

                if (clase == "arbol") {
                    d.padre[v] = u;
                    aristaPadre[v] = id;
                    d.tin[v] = reloj++;
                    pila.push_back(v);
                    registrar(TipoEvento::ENTRAR, v, -1, -1, d.tin[v], "");
                }
            } else {                                       // u sin más vecinos: salgo
                d.tout[u] = reloj++;
                pila.pop_back();
                d.ordenSalida.push_back(u);
                registrar(TipoEvento::SALIR, u, -1, -1, d.tout[u], "");
            }
        }
    }
    return d;
}

// ¿u es ancestro de v? O(1)   (u es ancestro de sí mismo)
bool esAncestro(int u, int v, const DFS& d) {
    return d.tin[u] <= d.tin[v] && d.tout[v] <= d.tout[u];
}

// Cantidad de vértices del subárbol de u. O(1)
// El reloj avanza 2 veces por vértice (entrar y salir).
int tamanoSubarbol(int u, const DFS& d) {
    return (d.tout[u] - d.tin[u] + 1) / 2;
}

// Orden topológico = orden de salida al revés. Solo válido sin ciclos.
vector<int> ordenTopologico(const Grafo& g, const DFS& d) {
    if (!g.dirigido || !d.ciclos.empty()) return {};
    vector<int> orden(d.ordenSalida.rbegin(), d.ordenSalida.rend());
    return orden;
}

// ---------------------------------------------------------------------
// Exportación a JSON (sin dependencias externas)
// ---------------------------------------------------------------------
static string jsonLista(const vector<int>& xs) {
    ostringstream o;
    o << "[";
    for (size_t i = 0; i < xs.size(); ++i) o << (i ? ", " : "") << xs[i];
    o << "]";
    return o.str();
}

static const char* nombreEvento(TipoEvento t) {
    switch (t) {
        case TipoEvento::NUEVO_ARBOL: return "nuevo_arbol";
        case TipoEvento::ENTRAR:      return "entrar";
        case TipoEvento::MIRAR:       return "mirar";
        case TipoEvento::SALIR:       return "salir";
    }
    return "?";
}

struct Consulta { int u, v; };

void exportarJSON(const string& ruta, const string& nombre, const Grafo& g,
                  const DFS& d, const vector<Consulta>& consultasAncestro,
                  const vector<int>& consultasSubarbol) {
    ofstream f(ruta);
    if (!f) { cerr << "No se pudo escribir " << ruta << "\n"; return; }

    f << "{\n";
    f << "  \"nombre\": \"" << nombre << "\",\n";
    f << "  \"n\": " << g.n << ",\n";
    f << "  \"dirigido\": " << (g.dirigido ? "true" : "false") << ",\n";

    f << "  \"aristas\": [\n";
    for (size_t i = 0; i < g.aristas.size(); ++i) {
        f << "    {\"id\": " << i << ", \"u\": " << g.aristas[i].first
          << ", \"v\": " << g.aristas[i].second
          << ", \"clase\": \"" << d.claseArista[i] << "\"}"
          << (i + 1 < g.aristas.size() ? "," : "") << "\n";
    }
    f << "  ],\n";

    f << "  \"eventos\": [\n";
    for (size_t i = 0; i < d.eventos.size(); ++i) {
        const Evento& e = d.eventos[i];
        f << "    {\"paso\": " << i << ", \"tipo\": \"" << nombreEvento(e.tipo)
          << "\", \"u\": " << e.u;
        if (e.tipo == TipoEvento::MIRAR)
            f << ", \"v\": " << e.v << ", \"arista\": " << e.arista
              << ", \"clase\": \"" << e.clase << "\"";
        if (e.tipo == TipoEvento::ENTRAR || e.tipo == TipoEvento::SALIR)
            f << ", \"t\": " << e.t;
        f << ", \"pila\": " << jsonLista(e.pila) << "}"
          << (i + 1 < d.eventos.size() ? "," : "") << "\n";
    }
    f << "  ],\n";

    f << "  \"vertices\": [\n";
    for (int u = 1; u <= g.n; ++u) {
        f << "    {\"id\": " << u << ", \"tin\": " << d.tin[u]
          << ", \"tout\": " << d.tout[u] << ", \"padre\": " << d.padre[u]
          << ", \"tam_subarbol\": " << tamanoSubarbol(u, d) << "}"
          << (u < g.n ? "," : "") << "\n";
    }
    f << "  ],\n";

    f << "  \"raices\": " << jsonLista(d.raices) << ",\n";
    f << "  \"orden_salida\": " << jsonLista(d.ordenSalida) << ",\n";

    vector<int> topo = ordenTopologico(g, d);
    f << "  \"orden_topologico\": "
      << (topo.empty() ? string("null") : jsonLista(topo)) << ",\n";

    f << "  \"ciclos\": [";
    for (size_t i = 0; i < d.ciclos.size(); ++i)
        f << (i ? ", " : "") << jsonLista(d.ciclos[i]);
    f << "],\n";

    f << "  \"consultas_ancestro\": [";
    for (size_t i = 0; i < consultasAncestro.size(); ++i) {
        int u = consultasAncestro[i].u;
        int v = consultasAncestro[i].v;
        f << (i ? ", " : "") << "{\"u\": " << u << ", \"v\": " << v
          << ", \"resultado\": " << (esAncestro(u, v, d) ? "true" : "false") << "}";
    }
    f << "],\n";

    f << "  \"consultas_subarbol\": [";
    for (size_t i = 0; i < consultasSubarbol.size(); ++i) {
        int u = consultasSubarbol[i];
        f << (i ? ", " : "") << "{\"u\": " << u
          << ", \"tamano\": " << tamanoSubarbol(u, d) << "}";
    }
    f << "]\n";
    f << "}\n";
}

// ---------------------------------------------------------------------
// Salida por consola (útil para el informe y para depurar)
// ---------------------------------------------------------------------
void imprimirResumen(const string& nombre, const Grafo& g, const DFS& d) {
    cout << "=== " << nombre << (g.dirigido ? " (dirigido)" : " (no dirigido)")
         << " ===\n";
    for (int u = 1; u <= g.n; ++u)
        cout << "  " << u << ": tin=" << d.tin[u] << " tout=" << d.tout[u]
             << " padre=" << d.padre[u] << "\n";
    cout << "  Aristas:\n";
    for (size_t i = 0; i < g.aristas.size(); ++i)
        cout << "    " << g.aristas[i].first << (g.dirigido ? " -> " : " - ")
             << g.aristas[i].second << " : " << d.claseArista[i] << "\n";
    cout << "  Arboles en el bosque: " << d.raices.size() << "\n";
    for (auto& c : d.ciclos) {
        cout << "  Ciclo:";
        for (int x : c) cout << " " << x;
        cout << "\n";
    }
    cout << "  Eventos registrados: " << d.eventos.size() << "\n\n";
}

// ---------------------------------------------------------------------
// Grafos de demostración
// ---------------------------------------------------------------------

// 1) Ejemplo de la clase (Semana 13, "Tiempos de entrada y salida").
//    Esperado: 1=1/14, 2=2/7, 3=3/6, 5=4/5, 4=8/13, 6=9/12, 7=10/11.
//    Retrocesos 5-2 y 7-4.
Grafo grafoClase() {
    Grafo g(7, false);
    int e[][2] = {{1,2},{1,4},{2,3},{2,5},{3,5},{4,6},{4,7},{6,7}};
    for (auto& a : e) g.agregarArista(a[0], a[1]);
    return g;
}

// 2) Desconectado: tres componentes -> bosque con tres árboles.
//    {1,2,3} triángulo, {4,5,6,7} árbol, {8} vértice aislado (caso borde).
Grafo grafoDesconectado() {
    Grafo g(8, false);
    int e[][2] = {{1,2},{2,3},{3,1},{4,5},{4,6},{6,7}};
    for (auto& a : e) g.agregarArista(a[0], a[1]);
    return g;
}

// 3) Dirigido con ciclo (mismo ejemplo de la clase, "Tipos de aristas").
//    Esperado: 1=1/6, 2=2/5, 3=3/4, 4=7/10, 5=8/9.
//    3->1 retroceso (ciclo 1->2->3->1), 1->3 avance, 4->2 cruce.
Grafo grafoDirigido() {
    Grafo g(5, true);
    int e[][2] = {{1,2},{1,3},{2,3},{3,1},{4,2},{4,5}};
    for (auto& a : e) g.agregarArista(a[0], a[1]);
    return g;
}

// 4) Caso real: un sistema jerárquico de carpetas (árbol, raíz 1).
// 1 Proyecto -> 2 Codigo (3 Algoritmos, 4 Pruebas),
//            -> 5 Datos (6 Imagenes), -> 7 Informe.
// Las aristas se guardan como no dirigidas para recorrer el árbol desde 1.
Grafo grafoCarpetas() {
    Grafo g(7, false);
    int e[][2] = {{1,2},{2,3},{2,4},{1,5},{5,6},{1,7}};
    for (auto& a : e) g.agregarArista(a[0], a[1]);
    return g;
}

// Verifica contra los valores de las diapositivas.
static void verificar(const DFS& d, const vector<pair<int,int>>& esperado) {
    for (size_t u = 1; u < esperado.size(); ++u) {
        assert(d.tin[u] == esperado[u].first);
        assert(d.tout[u] == esperado[u].second);
    }
}

int main(int argc, char** argv) {
    string dir = (argc > 1) ? string(argv[1]) : string(".");
    if (!dir.empty() && dir.back() != '/') dir += '/';

    // --- 1. Grafo de la clase ---
    Grafo g1 = grafoClase();
    DFS d1 = recorrerDFS(g1);
    verificar(d1, {{0,0},{1,14},{2,7},{3,6},{8,13},{4,5},{9,12},{10,11}});
    assert(esAncestro(1, 5, d1) && !esAncestro(2, 6, d1));
    assert(tamanoSubarbol(2, d1) == 3 && tamanoSubarbol(1, d1) == 7);
    imprimirResumen("Grafo de la clase", g1, d1);
    exportarJSON(dir + "grafo_clase.json", "Grafo de la clase", g1, d1,
                 {{1,5},{2,5},{2,6},{4,7},{3,3}}, {1,2,4,5});

    // --- 2. Grafo desconectado ---
    Grafo g2 = grafoDesconectado();
    DFS d2 = recorrerDFS(g2);
    assert(d2.raices.size() == 3);
    assert(d2.tin[8] + 1 == d2.tout[8] && tamanoSubarbol(8, d2) == 1);
    imprimirResumen("Grafo desconectado", g2, d2);
    exportarJSON(dir + "grafo_desconectado.json", "Grafo desconectado", g2, d2,
                 {{1,3},{1,4},{4,7},{8,8}}, {1,4,8});

    // --- 3. Grafo dirigido con ciclo ---
    Grafo g3 = grafoDirigido();
    DFS d3 = recorrerDFS(g3);
    verificar(d3, {{0,0},{1,6},{2,5},{3,4},{7,10},{8,9}});
    assert(d3.claseArista[3] == "retroceso");   // 3 -> 1
    assert(d3.claseArista[1] == "avance");      // 1 -> 3
    assert(d3.claseArista[4] == "cruce");       // 4 -> 2
    assert(d3.ciclos.size() == 1);
    imprimirResumen("Grafo dirigido con ciclo", g3, d3);
    exportarJSON(dir + "grafo_dirigido.json", "Grafo dirigido con ciclo", g3, d3,
                 {{1,3},{4,2},{4,5}}, {1,4});

    // --- 4. Aplicacion de la vida real: jerarquia de carpetas ---
    Grafo g4 = grafoCarpetas();
    DFS d4 = recorrerDFS(g4);
    verificar(d4, {{0,0},{1,14},{2,7},{3,4},{5,6},{8,11},{9,10},{12,13}});
    assert(esAncestro(2, 4, d4) && !esAncestro(2, 6, d4));
    assert(tamanoSubarbol(2, d4) == 3);
    imprimirResumen("Jerarquia de carpetas", g4, d4);
    exportarJSON(dir + "grafo_carpetas.json", "Jerarquia de carpetas", g4, d4,
                 {{2,4},{2,6},{1,7},{5,6}}, {1,2,5});

    cout << "Verificaciones OK. JSON generados en " << dir << "\n";
    return 0;
}
