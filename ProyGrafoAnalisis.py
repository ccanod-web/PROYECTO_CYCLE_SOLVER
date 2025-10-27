import networkx as nx
def camino_o_ciclo_euler(grafo):
    if len(grafo.nodes) == 0:
        return (False, False)
    if not nx.is_connected(grafo):
        return (False, False)
    grados_impares = sum(1 for _, deg in grafo.degree() if deg % 2 == 1)
    if grados_impares == 0:
        return (True, True)
    elif grados_impares == 2:
        return (False, True)
    else:
        return (False, False)
def camino_o_ciclo_hamilton(grafo):
    n = len(grafo.nodes)
    if n == 0:
        return (False, False)
    if n == 1:
        return (False, True)
    nodes = list(grafo.nodes)
    def existe_camino():
        for start in nodes:
            visited = {node: False for node in nodes}
            path = [start]
            visited[start] = True
            def backtrack(current):
                if len(path) == n:
                    return True
                for neighbor in grafo[current]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        path.append(neighbor)
                        if backtrack(neighbor):
                            return True
                        path.pop()
                        visited[neighbor] = False
                return False
            if backtrack(start):
                return True
        return False
    def existe_ciclo():
        if not nx.is_connected(grafo) or n < 3:
            return False
        start = nodes[0]
        visited = {node: False for node in nodes}
        path = [start]
        visited[start] = True
        def backtrack(current):
            if len(path) == n:
                return grafo.has_edge(path[-1], path[0])
            for neighbor in grafo[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    path.append(neighbor)
                    if backtrack(neighbor):
                        return True
                    path.pop()
                    visited[neighbor] = False
            return False
        return backtrack(start)
    tiene_camino = existe_camino()
    tiene_ciclo = existe_ciclo() if tiene_camino else False
    return (tiene_ciclo, tiene_camino)