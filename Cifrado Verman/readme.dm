Cifrado Vernam (One-Time Pad Simplificado)
Descripción

Este programa implementa el Cifrado Vernam, un cifrado de sustitución por clave aleatoria. Cada letra del mensaje se cifra sumando, módulo 26, un valor aleatorio de la clave generada, de forma que el mensaje resultante sea seguro mientras la clave sea secreta y del mismo tamaño que el mensaje.

El programa mantiene todas las letras en minúsculas y descarta caracteres no alfabéticos. Además, guarda el mensaje cifrado y la clave en un archivo temporal para su posterior descifrado, y elimina el archivo una vez finalizado el proceso.

Funcionalidades

Generación de clave pseudoaleatoria de la misma longitud que el mensaje.

Cifrado de un mensaje usando la clave (mod 26).

Descifrado del mensaje usando la misma clave.

Guardado y lectura del mensaje y la clave en un archivo temporal.

Eliminación automática del archivo de clave después del descifrado.
