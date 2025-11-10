# Hill Algorithm

En este programa implementamos el Cifrado Hill, un algoritmo de cifrado poligráfico basado en álgebra lineal. Utiliza una matriz cuadrada como clave para transformar bloques de texto en texto cifrado mediante multiplicación matricial modular.

Para cifrar, el texto se divide en vectores del mismo tamaño que la matriz clave, se multiplican por la matriz y se aplica módulo 26. Para descifrar, se utiliza la matriz inversa modular de la clave original.

---

## Ejecución

1. Abrimos la terminal y navegamos a la carpeta donde está el archivo `hill.py`.

```powershell
cd C:\ruta\a\la\carpeta
```

## Ejecutamos el programa con

python hill.py

## El programa mostrara el menu:

```powershell
=== CIFRADO HILL ===

Menú:
[1] Definir Matriz Clave
[2] Cifrar Mensaje
[3] Descifrar Mensaje
[4] Mostrar Matriz Actual
[5] Salir
Seleccione una opción:
```
Definir la Clave (Opción 1): Es el primer paso obligatorio. Ingresar la dimensión de la matriz (ej. 2 para 2x2) y luego sus elementos fila por fila separados por espacios. El programa validará si la matriz es invertible módulo 26.

Cifrar (Opción 2): Ingresar el mensaje a cifrar. 

Descifrar (Opción 3): Ingresar el texto cifrado para recuperar el mensaje original.

Verificar (Opción 4): Muestra la matriz clave actual y su inversa modular, útil para verificar los cálculos manuales.

