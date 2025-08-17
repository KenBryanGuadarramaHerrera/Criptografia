# Caesar Cipher Algorithm

Este programa implementa el **cifrado César**, un algoritmo clásico de sustitución que nos permite desplazar cada letra de un texto un número fijo de posiciones en el alfabeto. Nuestro alfabeto incluye **mayúsculas, minúsculas, la letra Ñ y las vocales acentuadas**.

Para cifrar, convertimos cada letra en su posición numérica, sumamos la **llave o desplazamiento n** que elijamos (un número entre 1 y 31) y luego volvemos a convertirla en letra, manteniendo los caracteres no alfabéticos sin cambios. Para descifrar, simplemente restamos la llave usando el mismo cálculo circular para no salirnos del alfabeto.

---

## Ejecución

1. Abrimos la terminal y navegamos a la carpeta donde está el archivo `Caesar.py`.

```powershell
cd C:\ruta\a\la\carpeta
```

## Ejecutamos el programa con

python Caesar.py

## El programa mostrara el menu:

Seleccionamos 1 para cifrar o 2 para descifrar.
Ingresamos el texto que queremos procesar.
Introducimos el desplazamiento n (1–31).
El programa nos mostrará el texto cifrado o descifrado en pantalla.


