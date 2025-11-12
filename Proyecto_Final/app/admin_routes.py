from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from functools import wraps # <--- ¡IMPORTAR ESTO!
from . import db
from .models import Survey, Option, Vote 
from .crypto.security import load_authority_public_key_text, verify_anonymous_signature # Importar las herramientas


admin_bp = Blueprint('admin', __name__)

# --- Decorador de Rol (Garantiza que solo Admins accedan) ---
def admin_required(f):
    """Decorador personalizado para restringir el acceso solo a administradores."""
    @wraps(f) # <--- APLICAR WRAPS AQUÍ
    @login_required
    def decorated_function(*args, **kwargs):
        # Asume que current_user tiene el método is_admin() definido en models.py
        if not current_user.is_admin():
            flash('Acceso denegado: Se requiere ser Administrador.', 'danger')
            return redirect(url_for('main.home')) 
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de Administración ---

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    """Panel principal del administrador."""
    surveys = Survey.query.all()
    return render_template('admin_dashboard.html', surveys=surveys)

@admin_bp.route('/admin/create_survey', methods=['GET', 'POST'])
@admin_required
def create_survey():
    """Permite al administrador crear una nueva encuesta y sus opciones."""
    if request.method == 'POST':
        title = request.form.get('title')
        options_list = request.form.getlist('option_text[]')

        if not title or len(options_list) < 2:
            flash('Se requiere un título y al menos dos opciones.', 'danger')
            return render_template('admin_create_survey.html')

        try:
            # 1. Crear la Encuesta
            new_survey = Survey(title=title, is_active=True)
            db.session.add(new_survey)
            db.session.flush() # Guarda el objeto para obtener su ID antes del commit

            # 2. Crear las Opciones
            for text in options_list:
                if text.strip():
                    new_option = Option(survey_id=new_survey.id, text=text.strip())
                    db.session.add(new_option)
            
            db.session.commit()
            flash(f'Encuesta "{title}" creada exitosamente.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la encuesta: {e}', 'danger')

    return render_template('admin_create_survey.html')


@admin_bp.route('/admin/results/<int:survey_id>')
@admin_required
def view_results(survey_id):
    """Muestra el conteo de votos y estadísticas para una encuesta, validando la firma anónima."""
    survey = db.session.get(Survey, survey_id)
    if not survey:
        abort(404)

    auth_public_pem = load_authority_public_key_text()
    if not auth_public_pem:
        flash('Error de configuración: Clave pública de la Autoridad no encontrada.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # 1. Obtener TODOS los votos
    all_votes = Vote.query.filter_by(survey_id=survey_id).all()
    
    valid_votes = []
    
    # 2. Verificar criptográficamente cada voto
    for vote in all_votes:
        # La verificación usa la Llave Pública del servidor y el hash original (no ciego)
        is_valid = verify_anonymous_signature(
            auth_public_pem,
            vote.vote_data_hash,
            vote.final_anonymous_signature
        )
        
        if is_valid:
            valid_votes.append(vote)

    # 3. Contar solo los votos válidos
    valid_vote_counts = {}
    for vote in valid_votes:
        valid_vote_counts[vote.option_id] = valid_vote_counts.get(vote.option_id, 0) + 1
        
    total_valid_votes = len(valid_votes)

    # 4. Preparar resultados finales
    results = Option.query.filter_by(survey_id=survey_id).all()
    stats = []
    
    for option in results:
        count = valid_vote_counts.get(option.id, 0)
        percentage = (count / total_valid_votes * 100) if total_valid_votes else 0
        stats.append({
            'text': option.text,
            'count': count,
            'percentage': f"{percentage:.2f}%"
        })

    flash(f'Total de votos procesados: {len(all_votes)}. Total de votos válidos contados: {total_valid_votes}.', 'info')
    
    return render_template('admin_results.html', survey=survey, stats=stats, total_votes=total_valid_votes)

@admin_bp.route('/admin/delete_survey/<int:survey_id>', methods=['POST'])
@admin_required
def delete_survey(survey_id):
    survey = db.session.get(Survey, survey_id)
    if not survey:
        flash('Encuesta no encontrada.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # ⚠️ PELIGRO: Esto requiere que SQLAlchemy elimine en cascada Opciones y Votos.
    # Si no tienes cascade configurado en models.py, esto fallará.
    db.session.delete(survey)
    db.session.commit()
    flash(f'Encuesta "{survey.title}" eliminada exitosamente.', 'success')
    return redirect(url_for('admin.dashboard'))