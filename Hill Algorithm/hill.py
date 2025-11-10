#-------------------------------------------------------------
# Nombre del programa: hill.py
# Descripción: Implementación del cifrado hill 
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

import numpy as np

#Función para encontrar el inverso modulo multiplicativo de a modulo m
def mod_inverse(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None
#Funcion para calcular la matriz inversa modular
def matrix_mod_inverse(matrix, modulus):
    det = int(np.round(np.linalg.det(matrix)))
    det_inv = mod_inverse(det, modulus)
    if det_inv is None:
        raise ValueError(f"La matriz no es invertible modulo {modulus} (MCD(det, {modulus}) != 1).")
    
    # Matriz adjunta usando la inversa estándar: adj(A) = det(A) * A^-1
    matrix_inv_standard = np.linalg.inv(matrix)
    adjugate_matrix = np.round(det * matrix_inv_standard).astype(int)
    
    # K^-1 = (det^-1 * adj(K)) mod m
    matrix_inv_mod = (det_inv * adjugate_matrix) % modulus
    return matrix_inv_mod.astype(int)

#Funcion para convertir texto a lista de numeros A =0, B=1...
def text_to_numbers(text):
    return [ord(char) - ord('A') for char in text.upper() if 'A' <= char <= 'Z']

#Funcion para convertir la lista de numeros a texto
def numbers_to_text(numbers):
    return ''.join(chr(int(num) + ord('A')) for num in numbers)

#Funcion para obtener la dimension y elementos de la matriz K
def get_key_matrix_from_user():
    while True:
        try:
            n = int(input("Ingrese la dimensión de la matriz cuadrada (ej. 2 para 2x2, 3 para 3x3): "))
            if n < 2:
                print("La dimensión debe ser al menos 2.")
                continue
            
            print(f"Ingrese los {n*n} elementos de la matriz fila por fila, separados por espacios (ej. 3 3 2 5): ")
            elements = list(map(int, input().split()))
            
            if len(elements) != n * n:
                print(f"Error: Se esperaban {n*n} elementos, pero se recibieron {len(elements)}.")
                continue
                
            key_matrix = np.array(elements).reshape(n, n)
            
            # Validar si es invertible módulo 26
            try:
                matrix_mod_inverse(key_matrix, 26)
                return key_matrix
            except ValueError as e:
                print(f"Error: {e} Por favor ingrese una matriz válida.")
                
        except ValueError:
            print("Entrada inválida. Por favor ingrese números enteros.")


def hill_encrypt(message, key_matrix):
    n = key_matrix.shape[0]
    msg_nums = text_to_numbers(message)
    
    # Relleno con 'X' si es necesario
    while len(msg_nums) % n != 0:
        msg_nums.append(ord('X') - ord('A'))
    
    msg_nums = np.array(msg_nums)
    blocks = msg_nums.reshape(-1, n).T
    encrypted_blocks = np.dot(key_matrix, blocks) % 26
    return numbers_to_text(encrypted_blocks.T.flatten())

def hill_decrypt(ciphertext, key_matrix):
    n = key_matrix.shape[0]
    key_matrix_inv = matrix_mod_inverse(key_matrix, 26)
    cipher_nums = np.array(text_to_numbers(ciphertext))
    
    # Asegurar que la longitud del texto cifrado sea múltiplo de n (debería serlo si fue cifrado correctamente)
    if len(cipher_nums) % n != 0:
         raise ValueError("Longitud del texto cifrado inválida para la matriz dada.")

    blocks = cipher_nums.reshape(-1, n).T
    decrypted_blocks = np.dot(key_matrix_inv, blocks) % 26
    return numbers_to_text(decrypted_blocks.T.flatten())


def main():
    print("=== CIFRADO HILL ===")
    key_matrix = None
    
    while True:
        print("\nMenú:")
        print("[1] Definir Matriz Clave")
        print("[2] Cifrar Mensaje")
        print("[3] Descifrar Mensaje")
        print("[4] Mostrar Matriz Actual")
        print("[5] Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            key_matrix = get_key_matrix_from_user()
            print("\nMatriz clave definida correctamente.")
            print(key_matrix)
            
        elif opcion == '2':
            if key_matrix is None:
                print("\nPrimero debe definir una matriz clave (Opción 1).")
                continue
            msg = input("Ingrese el mensaje a cifrar (solo letras A-Z): ")
            if not msg:
                 print("El mensaje no puede estar vacío")
                 continue
            encrypted = hill_encrypt(msg, key_matrix)
            print(f"\nMensaje Cifrado: {encrypted}")
            
        elif opcion == '3':
            if key_matrix is None:
                print("\nPrimero debe definir una matriz clave (Opción 1).")
                continue
            msg = input("Ingrese el mensaje cifrado a descifrar: ")
            if not msg:
                 print("El mensaje no puede estar vacío.")
                 continue
            try:
                decrypted = hill_decrypt(msg, key_matrix)
                print(f"\nMensaje Descifrado: {decrypted}")
            except ValueError as e:
                print(f"\nError durante el descifrado: {e}")

        elif opcion == '4':
             if key_matrix is not None:
                 print("\nMatriz Clave Actual:")
                 print(key_matrix)
                 try:
                     inv = matrix_mod_inverse(key_matrix, 26)
                     print("Matriz Inversa Modular (K^-1):")
                     print(inv)
                 except ValueError:
                     print("(No tiene inversa modular válida)")
             else:
                 print("\nNo hay matriz clave definida.")
                 
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()