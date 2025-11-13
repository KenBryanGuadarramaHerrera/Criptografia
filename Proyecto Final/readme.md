# Sistema de Votación Electrónica con Firma Ciega (RSA Blind Signature)

Este proyecto implementa una plataforma de votación electrónica segura, verificable y anónima utilizando **Python (Flask)**. El núcleo del sistema se basa en el protocolo criptográfico de **Firma Ciega de Chaum**, garantizando que la identidad del votante permanezca matemáticamente desvinculada de su voto (Unlinkability), mientras se asegura la elegibilidad y la integridad del sufragio.

## 📋 Tabla de Contenidos
- [Características Principales](#-características-principales)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Fundamentos Técnicos](#-fundamentos-técnicos)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Flujo de Uso](#-flujo-de-uso)
- [Autores](#-autores)

---

## Características Principales
* **Anonimato Absoluto:** Uso de Firmas Ciegas para separar identidad de voto.
* **Autenticación Fuerte (2FA):** Acceso mediante contraseña (Hash PBKDF2) + Archivo de Llave Privada (`.key`).
* **Integridad:** Hash `SHAKE128` y Firmas Digitales RSA-2048.
* **Anti-Replay:** Protección contra doble voto mediante restricciones de unicidad en base de datos.
* **Auditoría Pública:** Tablero de resultados con verificador de firmas criptográficas.

---

## 📂 Arquitectura del Proyecto

El sistema sigue una arquitectura modular basada en **MVC (Modelo-Vista-Controlador)**. A continuación se describe la estructura de carpetas y archivos:


/sistema_votacion
│
├── app.py                 # [CONTROLADOR] El cerebro del backend. Gestiona rutas,
│                          # sesiones, y orquesta la lógica entre la BD y la criptografía.
│
├── crypto_utils.py        # [MOTOR] Librería interna de utilidades criptográficas.
│                          # Contiene la lógica matemática de RSA, SHAKE128 y el
│                          # protocolo de cegado/descegado.
│
├── models.py              # [MODELO] Define el esquema de la Base de Datos (SQLAlchemy).
│                          # Gestiona las tablas 'User' y 'Vote' de forma aislada.
│
├── requirements.txt       # [DEPENDENCIAS] Lista de librerías necesarias.
│
├── static/                # [ASSETS] Archivos estáticos.
│   ├── style.css          # Hoja de estilos con diseño Institucional.
│   └── logo.png           # Recursos gráficos.
│
└── templates/             # [VISTA] Interfaz de usuario (HTML5).
    ├── index.html         # Portal de Login y Registro.
    ├── vote.html          # Cabina de votación (carga de llave .key).
    ├── results.html       # Tablero de auditoría y gráficas.
    ├── success.html       # Recibo digital de voto.
    ├── credits.html       # Créditos del equipo.
    └── how_it_works.html  # Documentación técnica integrada.

---

### Desde Relación de Módulos hasta el final


### Relación entre módulos

1.  **`app.py` (Controlador):** Recibe los datos del formulario web enviados desde los archivos en `templates/`.
2.  **`crypto_utils.py` (Lógica):** Es invocado por `app.py` para realizar operaciones matemáticas complejas (verificar firmas, cegar mensajes) sin ensuciar el código principal.
3.  **`models.py` (Datos):** Si la validación criptográfica es correcta, `app.py` almacena la información aquí.
    * *Nota de Seguridad:* `models.py` asegura que el usuario se guarde en una tabla y el voto en otra totalmente distinta, sin llaves foráneas que los unan.

---

## Fundamentos Técnicos

El protocolo de seguridad sigue estos pasos estrictos:

1.  **Registro:** Se generan un par de llaves RSA. La pública se guarda en el servidor, la privada se descarga al usuario (`.key`).
2.  **Cegado (Blinding):** El cliente genera un factor aleatorio $r$ y oculta su voto: $m' = (Hash(voto) \cdot r^e) \pmod n$.
3.  **Firma (Signing):** El servidor firma el mensaje cegado $m'$ sin ver el contenido: $s' = (m')^d \pmod n$.
4.  **Descegado (Unblinding):** El cliente remueve el factor $r$ para obtener una firma válida $s$ sobre el voto original.
5.  **Verificación:** La firma final $s$ cumple que $s^e \equiv Hash(voto) \pmod n$, probando su autenticidad.

---

##  Requisitos Previos

* **Python 3.8** o superior.
* **Pip** (Gestor de paquetes de Python).

---

##  Instalación y Ejecución

Sigue estos pasos para desplegar el proyecto localmente:

### 1. Clonar el repositorio
Descarga el código fuente o clona este repositorio.

### 2. Instalar dependencias
Navega a la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt

### 3. Ejecutar el Servidor
Inicia la aplicación Flask:
```bash
python app.py

### 4. Acceder
Abre tu navegador web e ingresa a:
`http://127.0.0.1:5000`

---

##  Flujo de Uso

1.  **Registro:** Ingrese usuario y contraseña en la pantalla principal. **Importante:** Guarde el archivo `.key` que se descargará automáticamente.
2.  **Votación:**
    * Acceda a "Ir a Votar".
    * Ingrese sus credenciales.
    * **Suba su archivo `.key`** (Factor de posesión).
    * Seleccione su opción y envíe.
3.  **Auditoría:**
    * Al votar, recibirá un **Recibo Digital (Hash)**. Copie este código.
    * Vaya a la sección de Resultados.
    * Use el buscador para verificar que su firma se encuentra en el registro inmutable.

---
