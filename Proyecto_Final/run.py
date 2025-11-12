from flask import Flask
from app import db, login_manager 
import os



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'una_clave_secreta_fuerte'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Cargar llaves de autoridad desde los archivos .pem
    base_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_dir, 'authority_private.pem'), 'rb') as f:
        app.config['AUTHORITY_PRIVATE_KEY'] = f.read()

    with open(os.path.join(base_dir, 'authority_public.pem'), 'rb') as f:
        app.config['AUTHORITY_PUBLIC_KEY'] = f.read()
    
    print("🔑 Llave privada cargada:", len(app.config['AUTHORITY_PRIVATE_KEY']), "bytes")
    print("🔑 Llave pública cargada:", len(app.config['AUTHORITY_PUBLIC_KEY']), "bytes")


    # Importar y registrar blueprints
    from app.auth_routes import auth_bp
    from app.main_routes import main_bp  # <--- NUEVA IMPORTACIÓN
    from app.voting_routes import voting_bp  # <--- NUEVA IMPORTACIÓN
    from app.admin_routes import admin_bp  # <--- NUEVA IMPORTACIÓN
    
    # 1. Rutas principales y autenticación
    app.register_blueprint(main_bp)      # <--- NUEVO REGISTRO
    app.register_blueprint(auth_bp)

    # 2. Funcionalidades específicas y portales
    app.register_blueprint(admin_bp)       # <--- NUEVO REGISTRO
    app.register_blueprint(voting_bp)      # <--- NUEVO REGISTRO
    

    # Crear tablas de la DB si no existen
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)