# -- coding: utf-8 --
"""
Implementación del cifrado de Vigenère sobre el alfabeto español (27 letras, incluyendo Ñ).
Incluimos además un ataque automático basado en el método de Kasiski y el análisis
de frecuencias (chi-cuadrado o método de Al-Kindi).

En esta implementación:

- Usamos módulo 27, ya que nuestro alfabeto contiene la Ñ.
- Conservamos mayúsculas y minúsculas tal como aparecen en el texto original.
- Copiamos los caracteres no alfabéticos sin modificarlos.
- Para romper el cifrado aplicamos:
    * El análisis de Kasiski, donde buscamos repeticiones y distancias para deducir
      la longitud probable de la clave.
    * El análisis de frecuencias con chi-cuadrado, donde comparamos el resultado
      de cada hipótesis con las frecuencias esperadas en español.
"""

MAX_LENGTH = 100000  # Límite informativo de longitud de texto

# ---------------------------------------------------------------------------
# Definimos el alfabeto español en mayúsculas y minúsculas.
# Incluimos la Ñ, lo que nos da un módulo de 27.
# ---------------------------------------------------------------------------

ALFABETO_MAY = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]
ALFABETO_MIN = [a.lower() for a in ALFABETO_MAY]
LONGITUD_ALFABETO = len(ALFABETO_MAY)  # 27 letras

# ---------------------------------------------------------------------------
# Definimos las frecuencias aproximadas de letras en español.
# Estas se usarán para evaluar hipótesis mediante chi-cuadrado.
# ---------------------------------------------------------------------------

FREC_ES = {
    'A':12.53,'B':1.49,'C':4.68,'D':5.86,'E':13.68,'F':0.69,'G':1.01,'H':0.70,'I':6.25,
    'J':0.44,'K':0.01,'L':4.97,'M':3.15,'N':7.01,'Ñ':0.31,'O':8.68,'P':2.51,'Q':0.88,
    'R':6.87,'S':7.98,'T':4.63,'U':3.93,'V':0.90,'W':0.01,'X':0.22,'Y':0.90,'Z':0.52
}

# ===========================================================================
# Funciones auxiliares para codificación y decodificación
# ===========================================================================

def codificar_caracter(c):
    """
    Convertimos un carácter 'c' en su índice dentro del alfabeto español (0..26).
    Si el carácter no pertenece al alfabeto definido, devolvemos -1.
    """
    if c in ALFABETO_MAY:
        return ALFABETO_MAY.index(c)
    if c in ALFABETO_MIN:
        return ALFABETO_MIN.index(c)
    return -1

def decodificar_posicion(pos, es_mayuscula):
    """
    Tomamos una posición 'pos' en el alfabeto (0..26) y la convertimos
    en un carácter. Si 'es_mayuscula' es True, devolvemos en mayúscula;
    de lo contrario, en minúscula.
    """
    if pos < 0 or pos >= LONGITUD_ALFABETO:
        return 'error'
    return ALFABETO_MAY[pos] if es_mayuscula else ALFABETO_MIN[pos]

def normaliza_clave(clave):
    """
    Normalizamos la clave:
    - Filtramos las letras que pertenecen a nuestro alfabeto (incluyendo Ñ).
    - Convertimos todo a mayúsculas para simplificar los cálculos.
    - Si la clave queda vacía, lanzamos un error.
    """
    filtrada = []
    for ch in clave:
        if ch in ALFABETO_MAY or ch in ALFABETO_MIN:
            filtrada.append(ch.upper())
    if not filtrada:
        raise ValueError("La clave debe contener al menos una letra del alfabeto español (incluida Ñ).")
    return ''.join(filtrada)

# ===========================================================================
# Implementación del cifrado y descifrado de Vigenère
# ===========================================================================

def vigenere_cifra(texto, clave):
    """
    Ciframos el texto con el algoritmo de Vigenère.
    - Usamos módulo 27.
    - Avanzamos sobre la clave únicamente en las letras (ignoramos espacios o signos).
    """
    claveN = normaliza_clave(clave)
    resultado = []
    j = 0
    for ch in texto:
        idx = codificar_caracter(ch)
        if idx == -1:
            resultado.append(ch)
            continue
        k = ALFABETO_MAY.index(claveN[j % len(claveN)])
        nueva = (idx + k) % LONGITUD_ALFABETO
        resultado.append(decodificar_posicion(nueva, ch in ALFABETO_MAY))
        j += 1
    return ''.join(resultado)

def vigenere_descifra(texto, clave):
    """
    Desciframos un texto con Vigenère.
    - Restamos el desplazamiento en módulo 27.
    - Conservamos mayúsculas y minúsculas.
    """
    claveN = normaliza_clave(clave)
    resultado = []
    j = 0
    for ch in texto:
        idx = codificar_caracter(ch)
        if idx == -1:
            resultado.append(ch)
            continue
        k = ALFABETO_MAY.index(claveN[j % len(claveN)])
        nueva = (idx - k) % LONGITUD_ALFABETO
        resultado.append(decodificar_posicion(nueva, ch in ALFABETO_MAY))
        j += 1
    return ''.join(resultado)

# ===========================================================================
# Análisis de Kasiski y frecuencias (ataque)
# ===========================================================================

from collections import defaultdict, Counter

def solo_letras_es(texto):
    """
    Extraemos únicamente las letras válidas (de nuestro alfabeto).
    Convertimos todo a mayúsculas para simplificar los cálculos.
    """
    res = []
    for ch in texto:
        if ch in ALFABETO_MAY:
            res.append(ch)
        elif ch in ALFABETO_MIN:
            res.append(ch.upper())
    return ''.join(res)

def encuentra_repeticiones(texto, min_len=3, max_len=5):
    """
    Buscamos repeticiones de substrings de longitud entre min_len y max_len.
    Calculamos las distancias entre apariciones consecutivas de esos substrings.
    """
    distancias = []
    for L in range(min_len, max_len+1):
        posiciones = defaultdict(list)
        for i in range(0, len(texto)-L+1):
            sub = texto[i:i+L]
            posiciones[sub].append(i)
        for inds in posiciones.values():
            if len(inds) >= 2:
                for a, b in zip(inds, inds[1:]):
                    distancias.append(b - a)
    return distancias

def factores(n):
    """
    Calculamos los factores mayores que 1 de un número n.
    Usamos esto para deducir longitudes posibles de la clave.
    """
    facs = set()
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            facs.add(i)
            facs.add(n//i)
    if n > 1:
        facs.add(n)
    return sorted(facs)

def candidatos_longitud_clave_por_kasiski(texto):
    """
    Aplicamos el método de Kasiski:
    - Encontramos distancias entre repeticiones.
    - Calculamos factores comunes.
    - Proponemos longitudes de clave más probables.
    """
    letras = solo_letras_es(texto)
    dists = encuentra_repeticiones(letras, 3, 5)
    if not dists:
        return []
    conteo = Counter()
    for d in dists:
        for f in factores(d):
            if 2 <= f <= 20:
                conteo[f] += 1
    return [k for k, _ in conteo.most_common(10)]

def chi_cuadrado_columna(texto_col):
    """
    Calculamos el estadístico chi-cuadrado comparando frecuencias observadas
    de una columna con las frecuencias esperadas en español.
    Mientras más bajo sea el valor, más parecido es al idioma.
    """
    N = len(texto_col)
    if N == 0: 
        return float('inf')
    obs = Counter(texto_col)
    chi = 0.0
    for letra in ALFABETO_MAY:
        Ei = FREC_ES[letra] * N / 100.0
        Oi = obs.get(letra, 0)
        if Ei > 0:
            chi += (Oi - Ei)**2 / Ei
    return chi

def mejor_desplazamiento_por_chi(columna):
    """
    Probamos todos los desplazamientos posibles en una columna
    y escogemos aquel que produce el menor chi-cuadrado.
    """
    mejor_shift = 0
    mejor_chi = float('inf')
    for s in range(LONGITUD_ALFABETO):
        desc = ''.join(ALFABETO_MAY[(ALFABETO_MAY.index(c) - s) % LONGITUD_ALFABETO] for c in columna)
        chi = chi_cuadrado_columna(desc)
        if chi < mejor_chi:
            mejor_chi = chi
            mejor_shift = s
    return mejor_shift, mejor_chi

def deduce_clave_por_frecuencias(cipher, m):
    """
    Dividimos el texto en m columnas y, para cada una, deducimos el mejor
    desplazamiento por chi-cuadrado. Reconstruimos la clave estimada.
    """
    columnas = ['' for _ in range(m)]
    solo = solo_letras_es(cipher)
    for i, ch in enumerate(solo):
        columnas[i % m] += ch
    shifts = []
    for col in columnas:
        s, _ = mejor_desplazamiento_por_chi(col)
        shifts.append(s)
    clave = ''.join(ALFABETO_MAY[s] for s in shifts)
    return clave

def puntua_texto_chi(texto):
    """
    Calculamos un puntaje chi-cuadrado global sobre todo el texto.
    Esto nos sirve para comparar hipótesis de clave completas.
    """
    plano = solo_letras_es(texto)
    return chi_cuadrado_columna(plano)

def rompe_vigenere_kasiski_frecuencias(cipher):
    """
    Intentamos romper un texto cifrado con Vigenère:
    1) Proponemos longitudes de clave con Kasiski.
    2) Para cada longitud, deducimos una clave por frecuencias.
    3) Desciframos y puntuamos con chi-cuadrado.
    4) Elegimos el mejor resultado.
    """
    candidatos = candidatos_longitud_clave_por_kasiski(cipher)
    if not candidatos:
        candidatos = list(range(2, 11))
    mejores = []
    for m in candidatos:
        try:
            clave_est = deduce_clave_por_frecuencias(cipher, m)
            claro = vigenere_descifra(cipher, clave_est)
            score = puntua_texto_chi(claro)
            mejores.append((score, clave_est, claro))
        except Exception:
            continue
    if not mejores:
        raise ValueError("No fue posible deducir la clave/descifrado.")
    mejores.sort(key=lambda x: x[0])
    return mejores[0]

# ===========================================================================
# Menú 
# ===========================================================================

def main():
    
    print(" --------- Vigenère --------- ")
    print("1. Cifrar con Vigenère")
    print("2. Descifrar con Vigenère")
    print("3. Romper (Kasiski + frecuencias)")
    opcion = input("Seleccione una opción (1/2/3): ").strip()

    if opcion in ('1', '2'):
        texto = input("Ingrese el texto: ")
        clave = input("Ingrese la clave (solo letras, puede incluir Ñ): ")
        if opcion == '1':
            print("\nTexto cifrado:\n", vigenere_cifra(texto, clave))
        else:
            print("\nTexto descifrado:\n", vigenere_descifra(texto, clave))
    elif opcion == '3':
        cipher = input("Ingrese el texto cifrado (Vigenère): ")
        score, clave, claro = rompe_vigenere_kasiski_frecuencias(cipher)
        print("\n--------- Resultado del ataque ---------")
        print("Clave estimada:", clave)
        print("Puntaje chi-cuadrado (menor es mejor):", round(score, 2))
        print("\nTexto descifrado (estimado):\n", claro)
    else:
        print("Opción inválida")

if __name__ == "__main__":
    main()
