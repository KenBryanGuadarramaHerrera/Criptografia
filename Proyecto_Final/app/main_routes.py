from flask import Blueprint, redirect, url_for, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Si el usuario está autenticado, lo enviamos a su dashboard/lista de encuestas
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('voting.active_surveys'))
    
    # 🛑 CORRECCIÓN: Si NO está autenticado, siempre lo enviamos a la página de LOGIN.
    # El login contendrá los enlaces para registrarse.
    return redirect(url_for('auth.login')) 


@main_bp.route('/home')
def home():
    """Ruta para la página de inicio, accesible sin login (muestra enlaces)."""
    # Si ya está autenticado, lo redirigimos fuera de esta página.
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('voting.active_surveys'))
            
    # Si no está autenticado, mostramos la plantilla con los enlaces de login/registro.
    return render_template('home.html')