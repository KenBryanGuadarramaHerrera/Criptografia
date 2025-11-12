# Importar db y login_manager desde el paquete app
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Almacena la llave pública como texto PEM. Se usará para verificar la firma del voto.
    public_key_pem = db.Column(db.Text, unique=True, nullable=True) 
    # Rol: 'user' o 'admin'
    role = db.Column(db.String(10), nullable=False, default='user')

    def set_password(self, password):
        """Hashea la contraseña para guardarla de forma segura."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña hasheada."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

# Loader para Flask-Login
from . import login_manager # Importar login_manager

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # Relación con las opciones
    options = db.relationship('Option', backref='survey', lazy=True)
    # Relación con los votos
    votes = db.relationship('Vote', backref='survey', lazy=True)
    
    def __repr__(self):
        return f'<Survey {self.title}>'

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    # No se guarda un contador aquí para forzar el conteo basado en votos únicos y seguros.
    
    def __repr__(self):
        return f'<Option {self.text}>'

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    
    # Datos de Seguridad/Criptografía:
    
    # 1. Hash del voto original (NO ES ÚNICO, varios usuarios pueden votar por la misma opción)
    vote_data_hash = db.Column(db.String(128), nullable=False)
    
    # 2. 🛑 CORRECCIÓN: Este campo era obligatorio antes, ahora no se usa en el nuevo flujo.
    # Debe ser nullable=True para no fallar.
    signature = db.Column(db.LargeBinary, nullable=True) # Antigua firma simple del votante
    
    # 3. Factor de cegado (necesario para rastrear)
    blind_factor = db.Column(db.Text, nullable=False) 
    
    # 4. Firma anónima final (resultado del descegado)
    final_anonymous_signature = db.Column(db.LargeBinary, nullable=False)
    
    # 5. Marcador (si aún se usa en tu lógica)
    has_signed_blind_vote = db.Column(db.Boolean, default=False)

    
    # Relaciones
    voter = db.relationship('User', backref='votes', lazy=True)
    
    def __repr__(self):
        return f'<Vote for {self.option_id} in {self.survey_id}>'
    
    

@login_manager.user_loader
def load_user(user_id):
    """Callback para recargar el objeto User desde el ID de sesión."""
    return db.session.get(User, int(user_id))