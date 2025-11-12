from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Survey, Vote, User 
from .crypto.security import hash_vote_data, sign_hash, verify_signature
from .crypto.security import (
    hash_vote_data, load_authority_private_key_text,
    load_authority_public_key_text,
    blind_hash, sign_blinded_hash, unblind_signature
)

voting_bp = Blueprint('voting', __name__)

# --- NUEVA RUTA: LISTA DE ENCUESTAS ACTIVAS ---
@voting_bp.route('/surveys')
@login_required
def active_surveys():
    """Muestra todas las encuestas activas disponibles para el usuario."""
    
    # 1. Obtener encuestas activas
    surveys = Survey.query.filter_by(is_active=True).all()
    
    # 2. Filtrar si el usuario ya votó (opcional, pero útil para la interfaz)
    # IDs de encuestas en las que el usuario ya votó
    voted_survey_ids = [vote.survey_id for vote in current_user.votes]
    
    # 3. Preparar lista final con el estado de votación
    surveys_with_status = []
    for survey in surveys:
        has_voted = survey.id in voted_survey_ids
        surveys_with_status.append({
            'survey': survey,
            'has_voted': has_voted
        })
    
    return render_template('user_survey_list.html', surveys_with_status=surveys_with_status)

# --- RUTA EXISTENTE: MOSTRAR FORMULARIO DE VOTO ---
@voting_bp.route('/vote/<int:survey_id>', methods=['GET'])
@login_required
def show_vote(survey_id):
    """Muestra la encuesta activa al usuario."""
    survey = db.session.get(Survey, survey_id)
    
    if not survey or not survey.is_active:
        flash('Encuesta no encontrada o inactiva.', 'danger')
        return redirect(url_for('voting.active_surveys')) # Redirigir a la lista

    # Verificar si el usuario ya votó
    if Vote.query.filter_by(user_id=current_user.id, survey_id=survey_id).first():
        flash('Ya has emitido tu voto para esta encuesta. No puedes volver a votar.', 'info')
        return redirect(url_for('voting.active_surveys')) # Redirigir a la lista
    
    return render_template('voting_form.html', survey=survey)

# --- RUTA EXISTENTE: PROCESAR VOTO ---
@voting_bp.route('/submit_vote', methods=['POST'])
@login_required
def submit_vote():
    # 1. Obtener datos y llaves
    survey_id = request.form.get('survey_id', type=int)
    option_id = request.form.get('option_id', type=int)
    private_key_pem_user = request.form.get('private_key_pem') 
    
    auth_public_pem = load_authority_public_key_text()
    auth_private_pem = load_authority_private_key_text()

    if not auth_public_pem or not auth_private_pem:
        flash('Error de configuración del servidor (Autoridad de Firma).', 'danger')
        return redirect(url_for('voting.active_surveys'))
    
    # 2. Verificar si el usuario ya votó
    if Vote.query.filter_by(user_id=current_user.id, survey_id=survey_id).first():
        flash('Ya has emitido tu voto para esta encuesta.', 'danger')
        return redirect(url_for('voting.active_surveys'))

    # 3. Datos del Voto (incluye user_id para autenticación/unicidad ANTES del cegado)
    vote_data = f"{survey_id}:{option_id}:{current_user.id}"
    vote_hash = hash_vote_data(vote_data)
    
    # 4. PASO DEL USUARIO (SIMULADO EN EL SERVIDOR): Cegado
    try:
        # El usuario ciega el voto con la llave pública del servidor
        blinded_hash_bytes, blinding_factor = blind_hash(auth_public_pem, vote_hash)
    except Exception as e:
        flash(f'Error de cegado: {e}', 'danger')
        return redirect(url_for('voting.show_vote', survey_id=survey_id))
    
    # 5. PASO DEL SERVIDOR: Firma del Hash Cegado (Aquí el servidor ve el voto ciego)
    try:
        # El servidor firma el hash ciego con su propia clave privada
        signed_blinded_hash_bytes = sign_blinded_hash(auth_private_pem, blinded_hash_bytes)
    except Exception as e:
        flash(f'Error de firma del servidor: {e}', 'danger')
        return redirect(url_for('voting.show_vote', survey_id=survey_id))

    # 6. PASO DEL USUARIO (SIMULADO EN EL SERVIDOR): Descegado
    try:
        # El usuario descega la firma con su factor de cegado
        final_anonymous_signature = unblind_signature(
            signed_blinded_hash_bytes, 
            blinding_factor, 
            auth_public_pem
        )
    except Exception as e:
        flash(f'Error de descegado: {e}', 'danger')
        return redirect(url_for('voting.show_vote', survey_id=survey_id))

    # 7. REGISTRO ANÓNIMO: Guardamos el voto con la firma anónima
    # 7. REGISTRO ANÓNIMO: Guardamos el voto
    new_vote = Vote(
        survey_id=survey_id,
        option_id=option_id,
        user_id=current_user.id, 
        vote_data_hash=vote_hash,
        # 🛑 ASIGNAR NONE O DEJAR QUE SQLAlchemy USE EL DEFAULT NULL si es nullable=True
        signature=None, # Asignamos None explícitamente si ya no se usa
        blind_factor=str(blinding_factor), 
        final_anonymous_signature=final_anonymous_signature,
        has_signed_blind_vote=True
    )
    db.session.add(new_vote)
    db.session.commit()
    flash('¡Voto registrado anónimamente y verificado exitosamente!', 'success')
    return redirect(url_for('voting.active_surveys'))