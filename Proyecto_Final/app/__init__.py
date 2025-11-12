from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar las extensiones aquí sin pasar la aplicación
db = SQLAlchemy()
login_manager = LoginManager()

# Opcionalmente, definir el user_loader aquí si no está en models.py
# @login_manager.user_loader
# def load_user(user_id):
#     from .models import User  # Importación local para evitar la dependencia circular
#     return db.session.get(User, int(user_id))