# -- coding: utf-8 --

MAX_LENGTH = 1000

# Alfabeto español en mayúsculas y minúsculas (incluye la Ñ, sin acentos)
ALFABETO_MAY = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]
ALFABETO_MIN = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

LONGITUD_ALFABETO = len(ALFABETO_MAY)  # 27


def codificar_caracter(c):
    # Tomamos un caracter c y devolvemos su posición en el alfabeto
    if c in ALFABETO_MAY:
        return ALFABETO_MAY.index(c)
    if c in ALFABETO_MIN:
        return ALFABETO_MIN.index(c)
    return -1  # Si no está en el alfabeto, retornamos -1


def decodificar_posicion(pos, es_mayuscula):
    if pos < 0 or pos >= LONGITUD_ALFABETO:
        return 'error'
    return ALFABETO_MAY[pos] if es_mayuscula else ALFABETO_MIN[pos]


def cifrar_cesar(texto, llave):
    resultado = ""
    for char in texto:
        codificacion = codificar_caracter(char)
        if codificacion != -1:
            nueva_pos = (codificacion + llave) % LONGITUD_ALFABETO
            es_mayus = char in ALFABETO_MAY
            resultado += decodificar_posicion(nueva_pos, es_mayus)
        else:
            resultado += char
    return resultado


def descifrar_cesar(texto, llave):
    resultado = ""
    for char in texto:
        codificacion = codificar_caracter(char)
        if codificacion != -1:
            nueva_pos = (codificacion - llave + LONGITUD_ALFABETO) % LONGITUD_ALFABETO
            es_mayus = char in ALFABETO_MAY
            resultado += decodificar_posicion(nueva_pos, es_mayus)
        else:
            resultado += char
    return resultado


def main():
    print(" --------- Cifrado César  --------- ")
    print("1. Cifrar")
    print("2. Descifrar")
    opcion = input("Seleccione una opción (1 o 2): ").strip()

    texto = input("Ingrese el texto: ")

    while True:
        try:
            llave = int(input("Ingrese el desplazamiento N (1-26): "))
            if 1 <= llave <= 26:
                break
            else:
                print("Error: La llave debe estar entre 1 y 26.")
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
