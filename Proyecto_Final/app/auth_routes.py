from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, session # <--- AGREGAR 'session'
from flask_login import login_user, current_user, logout_user
from .models import User, db
from . import db

# Imports necesarios para generar llaves y el ZIP
from io import BytesIO
import zipfile 
from .crypto.security import generate_rsa_key_pair, serialize_private_key, serialize_public_key


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. Verificar unicidad de username
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe. Por favor, elige otro.', 'danger')
            return redirect(url_for('auth.register'))
        
        # 2. Generar el par de llaves criptográficas
        try:
            private_key = generate_rsa_key_pair()
            private_pem = serialize_private_key(private_key)
            public_pem_str = serialize_public_key(private_key).decode('utf-8')
        except Exception as e:
            flash(f'Error al generar llaves: {e}', 'danger')
            return redirect(url_for('auth.register'))

        # 3. VALIDACIÓN CLAVE: Llave Pública Única (siempre improbable, pero seguro)
        if User.query.filter_by(public_key_pem=public_pem_str).first():
            flash('Error de integridad: La llave pública generada ya existe. Intente de nuevo.', 'danger')
            return redirect(url_for('auth.register'))

        # 4. Crear el nuevo usuario y asociar la Llave Pública
        new_user = User(
            username=username, 
            public_key_pem=public_pem_str,
            role='user' 
        )
        new_user.set_password(password)

        # 5. Guardar el usuario en la BD
        db.session.add(new_user)
        try:
            db.session.commit()
            
            # 6. DEVOLVER ZIP DIRECTO (sin usar sesión)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('private_key.pem', private_pem.decode('utf-8'))
                zipf.writestr('public_key_for_reference.pem', public_pem_str)
    
            zip_buffer.seek(0)
            return send_file(
                zip_buffer,
                mimetype='application/zip',
                as_attachment=True,
                download_name='voting_credentials.zip'
            )

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el usuario en la base de datos: {e}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')


@auth_bp.route('/register/success')
def success_and_download():
    """Muestra el mensaje de éxito y ofrece el botón de descarga y login."""
    # Necesitas la sesión para saber si hay llaves pendientes
    if 'private_pem_data' not in session:
        flash('No se encontraron datos de registro. Intente registrarse de nuevo.', 'danger')
        return redirect(url_for('auth.register'))
        
    # Necesitas crear la plantilla 'register_success.html' (código proporcionado antes)
    return render_template('register_success.html')


@auth_bp.route('/download-credentials')
def download_credentials():
    """Prepara y envía el archivo ZIP usando los datos de la sesión."""
    # session.pop() obtiene el dato Y lo elimina de la sesión, asegurando una sola descarga.
    private_pem_str = session.pop('private_pem_data', None) 
    public_pem_str = session.pop('public_pem_data', None)

    if not private_pem_str or not public_pem_str:
        flash('Error: Las credenciales ya han sido descargadas o caducaron.', 'danger')
        return redirect(url_for('auth.register'))
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('private_key.pem', private_pem_str.encode('utf-8'))
        zipf.writestr('public_key_for_reference.pem', public_pem_str.encode('utf-8'))
        
    zip_buffer.seek(0)
    
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='voting_credentials.zip'
    )

# Código para crear un administrador inicial
@auth_bp.route('/create-admin')
def create_initial_admin():
    from .models import User, db # Asegurar la importación si no está arriba
    
    if User.query.filter_by(role='admin').first():
        flash('Ya existe un administrador.', 'info')
        return redirect(url_for('auth.login'))

    # Crear el primer administrador con una llave pública simulada
    admin_user = User(username='admin', public_key_pem='ADMIN_KEY_SIMULADA', role='admin')
    admin_user.set_password('adminpassword') 
    db.session.add(admin_user)
    db.session.commit()
    flash('¡Administrador inicial creado! Usuario: admin, Contraseña: adminpassword', 'warning')
    return redirect(url_for('auth.login'))



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # ... (El resto de la función login se mantiene igual) ...
    # Asegúrate de que las importaciones de login_user y url_for estén arriba
    if current_user.is_authenticated:
        return redirect(url_for('main.home')) # o la ruta de dashboard/surveys si el user ya está logueado

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin():
                return redirect(url_for('admin.dashboard')) 
            else:
                # Redirigir a la lista de encuestas
                return redirect(url_for('voting.active_surveys')) 
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))