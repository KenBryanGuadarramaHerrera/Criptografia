# -------------------------------------------------------------
# Nombre del programa: cifradoVerman.py
# Descripción: Implementación del cifrado César para el alfabeto español
# Autor(es):
#    - Del Razo Sánchez Diego Adrián
#    - Guadarrama Herrera Ken Bryan
#    - Mendoza Espinosa Ricardo
#    - Vázquez Cárdenas Josué
#    - Villeda Tlecuitl José Eduardo
#    - Zavala Mendoza Luis Enrique
# Fecha de creación: 28/08/2025
# Última modificación: 28/08/2025
# Materia: Criptografía
# Versión: 1.0
# -------------------------------------------------------------
import random
import string

def generar_clave(longitud):
    """Generar una clave pseudoaleatoria de longitud igual al mensaje, usando números entre 0 y 25 mod 26."""
    clave = [random.randint(0, 25) for _ in range(longitud)]
    return clave

def cifrar_mensaje(mensaje, clave):
    """Cifrar el mensaje usando la clave generada (mod 26)"""
    mensaje_cifrado = []
    for i in range(len(mensaje)):
        # Convertir cada letra del mensaje a su valor en el alfabeto (0-25)
        valor_mensaje = ord(mensaje[i].lower()) - ord('a')
        
        # Realizar la operación de cifrado (suma modulo 26)
        valor_cifrado = (valor_mensaje + clave[i]) % 26
        
        # Convertir de nuevo al carácter cifrado (mantener minúsculas)
        mensaje_cifrado.append(chr(valor_cifrado + ord('a')))
    
    return ''.join(mensaje_cifrado)

def guardar_archivo(mensaje_cifrado, clave, nombre_archivo):
    """Guardar el mensaje cifrado y la clave en un archivo"""
    with open(nombre_archivo, 'w') as archivo:
        archivo.write(f"{mensaje_cifrado}\n")
        archivo.write(f"{','.join(map(str, clave))}\n")

def recibir_archivo(nombre_archivo):
    """Recibir el archivo y leer el mensaje cifrado y la clave"""
    with open(nombre_archivo, 'r') as archivo:
        mensaje_cifrado = archivo.readline().strip()
        clave = list(map(int, archivo.readline().strip().split(',')))
    return mensaje_cifrado, clave

def descifrar_mensaje(mensaje_cifrado, clave):
    """Descifrar el mensaje utilizando la clave (mod 26)"""
    mensaje_descifrado = []
    for i in range(len(mensaje_cifrado)):
        # Convertir cada letra del mensaje cifrado a su valor en el alfabeto
        valor_cifrado = ord(mensaje_cifrado[i].lower()) - ord('a')
        
        # Realizar la operación de descifrado (restar la clave y aplicar mod 26)
        valor_descifrado = (valor_cifrado - clave[i]) % 26
        
        # Convertir de nuevo al carácter descifrado (mantener minúsculas)
        mensaje_descifrado.append(chr(valor_descifrado + ord('a')))
    
    return ''.join(mensaje_descifrado)

def eliminar_archivo(nombre_archivo):
    """Eliminar el archivo que contiene la clave"""
    import os
    os.remove(nombre_archivo)

# Procedimiento principal
def proceso_cifrado():
    # Paso 1: Recibir mensaje (M)
    mensaje = input("Introduce el mensaje a cifrar (solo letras): ").lower()
    
    # Paso 2: Calcular la longitud del mensaje
    LM = len(mensaje)
    
    # Paso 3: Generar clave K (números aleatorios mod 26)
    clave = generar_clave(LM)
    
    # Paso 4: Cifrar el mensaje
    mensaje_cifrado = cifrar_mensaje(mensaje, clave)
    
    # Paso 5: Guardar mensaje cifrado y clave en un archivo
    nombre_archivo = "mensaje_clave.txt"
    guardar_archivo(mensaje_cifrado, clave, nombre_archivo)
    
    # Mostrar mensaje cifrado
    print(f"Mensaje cifrado: {mensaje_cifrado}")
    
    # Paso 6: Recibir el archivo y leer los datos
    mensaje_cifrado_recibido, clave_recibida = recibir_archivo(nombre_archivo)
    
    # Paso 7: Descifrar el mensaje
    mensaje_descifrado = descifrar_mensaje(mensaje_cifrado_recibido, clave_recibida)
    print(f"Mensaje original: {mensaje_descifrado}")
    
    # Paso 8: Eliminar el archivo de clave
    eliminar_archivo(nombre_archivo)
    print(f"El archivo {nombre_archivo} ha sido eliminado.")

# Ejecutar el proceso
proceso_cifrado()
