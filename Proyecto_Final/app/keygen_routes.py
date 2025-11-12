from flask import Blueprint, render_template, send_file, request, flash, redirect, url_for
from io import BytesIO
import zipfile # <--- ¡Nueva Importación!
from .crypto.security import generate_rsa_key_pair, serialize_private_key, serialize_public_key

keygen_bp = Blueprint('keygen', __name__, url_prefix='/keygen')

@keygen_bp.route('/register/keys')
def register_keys_form():
    """Muestra el formulario de generación de llaves."""
    # En un proyecto real, esto se combinaría con el registro de usuario
    return render_template('register_keys.html')

@keygen_bp.route('/generate-credentials', methods=['POST'])
def generate_credentials():
    """Genera el par de llaves, las comprime en un ZIP y lo descarga."""
    try:
        # 1. Generar el par de llaves
        private_key = generate_rsa_key_pair()
        
        # 2. Serializar ambas llaves a formato bytes
        private_pem = serialize_private_key(private_key)
        public_pem = serialize_public_key(private_key)
        
        # 3. Crear un archivo ZIP en memoria (BytesIO)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Añadir la llave privada
            zipf.writestr('private_key.pem', private_pem)
            # Añadir la llave pública
            zipf.writestr('public_key.pem', public_pem)
            
        # 4. Preparar la respuesta para la descarga del ZIP
        zip_buffer.seek(0)
        
        flash('Llaves generadas. Descargue el archivo ZIP y guarde su Llave Pública para el registro.', 'success')

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='voting_credentials.zip'
        )

    except Exception as e:
        # Ahora el error se lanza en el navegador como un flash
        flash(f'Ocurrió un error al generar las llaves: {e}', 'danger')
        return redirect(url_for('keygen.register_keys_form'))