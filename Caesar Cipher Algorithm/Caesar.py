# -- coding: utf-8 --

MAX_LENGTH = 1000

# Alfabeto en mayúsculas y minúsculas con Ñ y vocales acentuadas
ALFABETO_MAY = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'Ñ',
    'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'Á', 'É', 'Í', 'Ó', 'Ú'
]
ALFABETO_MIN = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ',
    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'á', 'é', 'í', 'ó', 'ú'
]

LONGITUD_ALFABETO = len(ALFABETO_MAY)  # 32


def codificar_caracter(c):
    #Tomamos un caracter c y devolvemos su posicion en el alfabeto
    #Usamos las listas ALFABETO_MAY y ALFABETO_MIN para incluir A-Z, Ñ, y vocales acentuadas
    if c in ALFABETO_MAY:
        return ALFABETO_MAY.index(c)
    if c in ALFABETO_MIN:
        return ALFABETO_MIN.index(c)
    return -1 #Si no esta el caracter en el alfabeto, retornamos el error

# pos = posicion, es_mayuscula = un tipo de letra
def decodificar_posicion(pos, es_mayuscula):
    if pos < 0 or pos >= LONGITUD_ALFABETO:
        return 'error' #Si la posicion esta fuera del rango retornamos error
    return ALFABETO_MAY[pos] if es_mayuscula else ALFABETO_MIN[pos]


def cifrar_cesar(texto, llave):
    resultado = ""
    #Iteramos en cada caracter del texto, obtenemos su posicion en el alfabeto
    for char in texto:
        codificacion = codificar_caracter(char)
        if codificacion != -1:
            #Sumamos la llave (el desplazamiento n) y aplicamos modulo para mantener dentro del rango del alfabeto
            nueva_pos = (codificacion + llave) % LONGITUD_ALFABETO
            es_mayus = char in ALFABETO_MAY
            #Usamos decodificar_posicion para obtener la letra cifrada.
            resultado += decodificar_posicion(nueva_pos, es_mayus)
        else:
            resultado += char #Si no se encuentra el caracter en el alfabeto, lo agregamos tal cual
                              # x ejemplo espacios, numeros, signos
    return resultado


def descifrar_cesar(texto, llave):
    #De forma analogica al cifrado, pero ahora restamos la llave en vez de sumarla
    resultado = ""
    for char in texto:
        codificacion = codificar_caracter(char)
        if codificacion != -1:
            #Sumamos LONGITUD_ALFABETO para asegurar que el resultado no sea negativo
            nueva_pos = (codificacion - llave + LONGITUD_ALFABETO) % LONGITUD_ALFABETO
            es_mayus = char in ALFABETO_MAY
            resultado += decodificar_posicion(nueva_pos, es_mayus)
        else:
            resultado += char
    return resultado


def main():
    print(" --------- Cifrado César con Ñ y acentos --------- ")
    print("1. Cifrar")
    print("2. Descifrar")
    opcion = input("Seleccione una opción (1 o 2): ").strip()

    texto = input("Ingrese el texto: ")

    while True:
        try:
            llave = int(input("Ingrese el desplazamiento N (1-31): "))
            if 1 <= llave <= 31:
                break
            else:
                print("Error: La llave debe estar entre 1 y 31.")
        except ValueError:
            print("Error: Ingrese un número válido.")

    if opcion == '1':
        resultado = cifrar_cesar(texto, llave)
        print("\nTexto cifrado:", resultado)
    elif opcion == '2':
        resultado = descifrar_cesar(texto, llave)
        print("\nTexto descifrado:", resultado)
    else:
        print("Opción inválida")


if __name__ == "__main__":
    main()
