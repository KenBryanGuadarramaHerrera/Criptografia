import string

# Crear la matriz 5x5
def crear_matriz(clave):
    alfabeto = string.ascii_lowercase.replace('j', '')  # Eliminar 'j' para evitar duplicados con 'i'
    clave = ''.join(sorted(set(clave), key=lambda x: clave.index(x)))  # Eliminar duplicados de la clave
    clave = clave.replace('j', 'i')  # Tratar 'j' como 'i'
    clave = ''.join([char for char in clave if char in alfabeto])  # Mantener solo caracteres válidos
    cadena_matriz = clave + alfabeto  # Agregar el resto del alfabeto
    cadena_matriz = ''.join(sorted(set(cadena_matriz), key=lambda x: cadena_matriz.index(x)))  # Eliminar duplicados
    matriz = [cadena_matriz[i:i+5] for i in range(0, 25, 5)]
    return matriz

# Encontrar la posición de una letra en la matriz
def encontrar_posicion(matriz, char):
    for fila in range(5):
        for col in range(5):
            if matriz[fila][col] == char:
                return fila, col
    return None, None

# Preprocesar el mensaje
def preprocesar_mensaje(mensaje):
    mensaje = mensaje.lower().replace('j', 'i')  # Tratar 'j' como 'i'
    mensaje = ''.join([char for char in mensaje if char in string.ascii_lowercase])  # Mantener solo letras
    if len(mensaje) % 2 != 0:  # Agregar 'x' si la longitud del mensaje es impar
        mensaje += 'x'
    pares = []
    i = 0
    while i < len(mensaje):
        if i + 1 < len(mensaje) and mensaje[i] == mensaje[i + 1]:  # Insertar 'x' entre letras repetidas
            pares.append(mensaje[i] + 'x')
            i += 1
        else:
            pares.append(mensaje[i:i + 2])
            i += 2
    return pares

# Cifrar un par de letras
def cifrar_par(par, matriz):
    f1, c1 = encontrar_posicion(matriz, par[0])
    f2, c2 = encontrar_posicion(matriz, par[1])
    if f1 == f2:  # Mismas fila: desplazar a la derecha
        return matriz[f1][(c1 + 1) % 5] + matriz[f2][(c2 + 1) % 5]
    elif c1 == c2:  # Mismas columna: desplazar hacia abajo
        return matriz[(f1 + 1) % 5][c1] + matriz[(f2 + 1) % 5][c2]
    else:  # Diferentes filas y columnas: formar un rectángulo
        return matriz[f1][c2] + matriz[f2][c1]

# Cifrar el mensaje
def cifrar_wheatstone(clave, mensaje):
    matriz = crear_matriz(clave)
    pares = preprocesar_mensaje(mensaje)
    mensaje_cifrado = ''.join([cifrar_par(par, matriz) for par in pares])
    return mensaje_cifrado

# Ejemplo de uso
clave = "kamikaze"
mensaje = "Hola mundo aquí estoy"
mensaje_cifrado = cifrar_wheatstone(clave, mensaje)
print("Mensaje Cifrado:", mensaje_cifrado)
