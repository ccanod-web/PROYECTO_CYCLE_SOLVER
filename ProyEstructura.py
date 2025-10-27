from flask import Flask, render_template, request, Response
import os
import csv
import sqlite3
import ast
import matplotlib.pyplot as plt
from io import StringIO
import networkx as nx
import ProyGrafoGuardar
import ProyGrafoAnalisis
app = Flask(__name__)
if not os.path.exists('static'):
    os.makedirs('static')
def limpiar_aristas(input_str):
    input_str = input_str.strip()
    if not input_str:
        raise ValueError("Aristas vacías.")
    if not (input_str.startswith('(') or input_str.startswith('[')):
        input_str = "[" + input_str + "]"
    else:
        if input_str.startswith('(') and not input_str.startswith('(('):
            input_str = "[" + input_str + "]"
    import re
    input_str = re.sub(r'\s+', ' ', input_str)
    return input_str
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            nombre = request.form.get("nombre", "").strip()
            nodos_input = request.form.get("nodos", "").strip()
            aristas_input = request.form.get("aristas", "").strip()
            if not nombre or not nodos_input or not aristas_input:
                return "<h1 style='color:red;'>Debe llenar todos los campos.</h1><br><a href='/'>Volver</a>"
            try:
                nodos_lista = [int(x.strip()) for x in nodos_input.split(",") if x.strip()]
                if not nodos_lista:
                    raise ValueError("La lista de nodos no es válida.")
                aristas_str = limpiar_aristas(aristas_input)
                aristas_lista = ast.literal_eval(aristas_str)
                if not isinstance(aristas_lista, list):
                    raise ValueError("Las aristas deben ser una lista de pares.")
                for edge in aristas_lista:
                    if not (isinstance(edge, (tuple, list)) and len(edge) == 2):
                        raise ValueError(f"Arista inválida: {edge}. Debe tener dos elementos.")
                    if not all(isinstance(x, int) for x in edge):
                        raise ValueError(f"Arista contiene valores no enteros: {edge}.")
                nodos_set = set(nodos_lista)
                for u, v in aristas_lista:
                    if u not in nodos_set or v not in nodos_set:
                        raise ValueError(f"Arista ({u},{v}) contiene nodos no declarados.")
                G = nx.Graph()
                G.add_nodes_from(nodos_lista)
                G.add_edges_from(aristas_lista)
                euler_ciclo, euler_camino = ProyGrafoAnalisis.camino_o_ciclo_euler(G)
                hamilton_ciclo, hamilton_camino = ProyGrafoAnalisis.camino_o_ciclo_hamilton(G)
                ProyGrafoGuardar.guardar_grafos(
                    nombre, G,
                    euler_ciclo, euler_camino,
                    hamilton_ciclo, hamilton_camino
                )
                with sqlite3.connect("proy_grafos.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM ejercicios ORDER BY id DESC LIMIT 1")
                    row = cursor.fetchone()
                    ultimo_id = row[0] if row else 1

                img_filename = f"grafo_{ultimo_id}.png"
                img_path = os.path.join("static", img_filename)
                plt.figure(figsize=(6, 6))
                pos = nx.spring_layout(G, seed=42)
                nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray',
                        node_size=500, font_size=16)
                plt.title(f"Grafo #{ultimo_id}", fontsize=14)
                plt.savefig(img_path, dpi=100, bbox_inches='tight')
                plt.close()
                return render_template(
                    "ProyResultados.html",
                    euler_ciclo=euler_ciclo,
                    euler_camino=euler_camino,
                    hamilton_ciclo=hamilton_ciclo,
                    hamilton_camino=hamilton_camino,
                    grafo_id=ultimo_id
                )
            except Exception as e:
                return f"<h1 style='color:red;'>Error: {str(e)}</h1><br><a href='/'>Volver</a>"
        return render_template("ProyInicio.html")
    except Exception as e:
        return f"<h1 style='color:red;'>Error: {str(e)}</h1><br><a href='/'>Volver</a>"
@app.route("/historial")
def historial():
    with sqlite3.connect("proy_grafos.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ejercicios ORDER BY fecha DESC")
        registros = cursor.fetchall()
    return render_template("ProyHistorial.html", registros=registros)
@app.route("/descargar_csv")
def descargar_csv():
    with sqlite3.connect("proy_grafos.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ejercicios ORDER BY fecha DESC")
        registros = cursor.fetchall()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "ID", "Nombre", "Nodos", "Aristas",
        "Ciclo Euler", "Camino Euler",
        "Ciclo Hamilton", "Camino Hamilton",
        "Fecha"
    ])
    for r in registros:
        writer.writerow([
            r["id"],
            r["nombre"],
            r["nodos"],
            r["aristas"],
            "Sí" if r["ciclo_euler"] else "No",
            "Sí" if r["camino_euler"] else "No",
            "Sí" if r["ciclo_hamilton"] else "No",
            "Sí" if r["camino_hamilton"] else "No",
            r["fecha"]
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=historial_grafos.csv"}
    )
if __name__ == "__main__":
    ProyGrafoGuardar.tabla_grafos()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)