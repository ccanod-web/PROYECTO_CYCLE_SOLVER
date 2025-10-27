import sqlite3
import datetime
def tabla_grafos():
    with sqlite3.connect("proy_grafos.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ejercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                nodos TEXT NOT NULL,
                aristas TEXT NOT NULL,
                ciclo_euler BOOLEAN NOT NULL,
                camino_euler BOOLEAN NOT NULL,
                ciclo_hamilton BOOLEAN NOT NULL,
                camino_hamilton BOOLEAN NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
def guardar_grafos(nombre, grafo, euler_ciclo, euler_camino, hamilton_ciclo, hamilton_camino):
    nodos = str(list(grafo.nodes))
    aristas = str(list(grafo.edges))
    fecha_utc = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect("proy_grafos.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ejercicios (
                nombre, nodos, aristas,
                ciclo_euler, camino_euler,
                ciclo_hamilton, camino_hamilton,
                fecha
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nombre, nodos, aristas,
            euler_ciclo, euler_camino,
            hamilton_ciclo, hamilton_camino,
            fecha_utc
        ))
        conn.commit()