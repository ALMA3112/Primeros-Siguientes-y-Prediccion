EPSILON = 'ε'   
FIN = '$'       


def cargar_gramatica(nombre_archivo="Gramatica.txt"):
    gramatica = {}
    inicial = None
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or "->" not in linea:
                    continue
                izquierda, derecha = linea.split("->", 1)
                izquierda = izquierda.strip()
                if inicial is None:
                    inicial = izquierda
                derecha = derecha.strip()
                if derecha == "":
                    produccion = [EPSILON]
                else:
                    produccion = derecha.split()
                    if len(produccion) == 0:
                        produccion = [EPSILON]
                if izquierda not in gramatica:
                    gramatica[izquierda] = []
                gramatica[izquierda].append(produccion)
    except FileNotFoundError:
        raise SystemExit(f"Error: no se encontró el archivo '{nombre_archivo}'.")
    if inicial is None:
        raise SystemExit("Error: no se detectaron producciones en el archivo.")
    return gramatica, inicial

def obtener_simbolos(gramatica):
    no_terminales = set(gramatica.keys())
    terminales = set()
    for cabeza, producciones in gramatica.items():
        for prod in producciones:
            for simbolo in prod:
                if simbolo != EPSILON and simbolo not in no_terminales:
                    terminales.add(simbolo)
    return terminales, no_terminales

def calcular_primeros(gramatica, terminales, no_terminales):
    primeros = {nt: set() for nt in gramatica}

    cambiado = True
    while cambiado:
        cambiado = False
        for cabeza, producciones in gramatica.items():
            for prod in producciones:
                # caso directo con epsilon
                if len(prod) == 1 and prod[0] == EPSILON:
                    if EPSILON not in primeros[cabeza]:
                        primeros[cabeza].add(EPSILON)
                        cambiado = True
                    continue

                puede_epsilon = True
                for simbolo in prod:
                    if simbolo == EPSILON:
                        if EPSILON not in primeros[cabeza]:
                            primeros[cabeza].add(EPSILON)
                            cambiado = True
                        puede_epsilon = False
                        break
                    if simbolo in terminales:
                        if simbolo not in primeros[cabeza]:
                            primeros[cabeza].add(simbolo)
                            cambiado = True
                        puede_epsilon = False
                        break
                    else:
                        antes = len(primeros[cabeza])
                        for t in primeros[simbolo]:
                            if t != EPSILON:
                                primeros[cabeza].add(t)
                        if len(primeros[cabeza]) != antes:
                            cambiado = True
                        if EPSILON in primeros[simbolo]:
                            puede_epsilon = True
                        else:
                            puede_epsilon = False
                            break
                if puede_epsilon:
                    if EPSILON not in primeros[cabeza]:
                        primeros[cabeza].add(EPSILON)
                        cambiado = True
    return primeros

def calcular_siguientes(gramatica, primeros, inicial, terminales, no_terminales):
    siguientes = {nt: set() for nt in gramatica}
    siguientes[inicial].add(FIN)

    cambiado = True
    while cambiado:
        cambiado = False
        for cabeza, producciones in gramatica.items():
            for prod in producciones:
                for i, B in enumerate(prod):
                    if B not in no_terminales:
                        continue
                    beta = prod[i+1:]
                    primeros_beta = set()
                    if len(beta) == 0:
                        primeros_beta.add(EPSILON)
                    else:
                        puede_epsilon = True
                        for s in beta:
                            if s == EPSILON:
                                primeros_beta.add(EPSILON)
                                puede_epsilon = False
                                break
                            if s in terminales:
                                primeros_beta.add(s)
                                puede_epsilon = False
                                break
                            else:
                                for t in primeros[s]:
                                    if t != EPSILON:
                                        primeros_beta.add(t)
                                if EPSILON in primeros[s]:
                                    puede_epsilon = True
                                else:
                                    puede_epsilon = False
                                    break
                        if puede_epsilon:
                            primeros_beta.add(EPSILON)

                    antes = len(siguientes[B])
                    for t in primeros_beta:
                        if t != EPSILON:
                            siguientes[B].add(t)
                    if len(siguientes[B]) != antes:
                        cambiado = True

                    if EPSILON in primeros_beta:
                        antes = len(siguientes[B])
                        for t in siguientes[cabeza]:
                            siguientes[B].add(t)
                        if len(siguientes[B]) != antes:
                            cambiado = True
    return siguientes

def calcular_prediccion(gramatica, primeros, siguientes, terminales, no_terminales):
    predicciones = {}
    for cabeza, producciones in gramatica.items():
        predicciones[cabeza] = []
        for prod in producciones:
            primeros_alpha = set()
            if len(prod) == 1 and prod[0] == EPSILON:
                primeros_alpha.add(EPSILON)
            else:
                puede_epsilon = True
                for s in prod:
                    if s == EPSILON:
                        primeros_alpha.add(EPSILON)
                        puede_epsilon = False
                        break
                    if s in terminales:
                        primeros_alpha.add(s)
                        puede_epsilon = False
                        break
                    else:
                        for t in primeros[s]:
                            if t != EPSILON:
                                primeros_alpha.add(t)
                        if EPSILON in primeros[s]:
                            puede_epsilon = True
                        else:
                            puede_epsilon = False
                            break
                if puede_epsilon:
                    primeros_alpha.add(EPSILON)

            pred = set()
            for t in primeros_alpha:
                if t != EPSILON:
                    pred.add(t)
            if EPSILON in primeros_alpha:
                for t in siguientes[cabeza]:
                    pred.add(t)
            predicciones[cabeza].append((prod, pred))
    return predicciones

def mostrar_resultados(gramatica, inicial, primeros, siguientes, predicciones):
    print("Símbolo inicial:", inicial)
    print("\nProducciones:")
    for nt in gramatica:
        for p in gramatica[nt]:
            print(f"  {nt} -> {' '.join(p)}")

    print("\nPRIMEROS")
    for nt in gramatica:
        conjunto = sorted(list(primeros[nt]))
        print(f"Primeros({nt}) = {{ {', '.join(conjunto)} }}")

    print("\nSIGUIENTES")
    for nt in gramatica:
        conjunto = sorted(list(siguientes[nt]))
        print(f"Siguientes({nt}) = {{ {', '.join(conjunto)} }}")

    print("\nPREDICCION")
    for nt in gramatica:
        for prod, pred in predicciones[nt]:
            prod_str = ' '.join(prod)
            conjunto = sorted(list(pred))
            print(f"Prediccion({nt} -> {prod_str}) = {{ {', '.join(conjunto)} }}")

if __name__ == "__main__":
    archivo = input("Ingrese el nombre del archivo de gramatica : Gramatica.txt o Gramatica2.txt: ")
    gramatica, inicial = cargar_gramatica(archivo)
    
    terminales, no_terminales = obtener_simbolos(gramatica)
    primeros = calcular_primeros(gramatica, terminales, no_terminales)
    siguientes = calcular_siguientes(gramatica, primeros, inicial, terminales, no_terminales)
    predicciones = calcular_prediccion(gramatica, primeros, siguientes, terminales, no_terminales)

    mostrar_resultados(gramatica, inicial, primeros, siguientes, predicciones)

