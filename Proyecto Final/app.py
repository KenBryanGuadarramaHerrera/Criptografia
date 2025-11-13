from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from models import db, User, Vote
from crypto_utils import CryptoManager
from collections import Counter  # <--- Agrega esto junto a los otros imports
from werkzeug.security import generate_password_hash, check_password_hash
from Crypto.PublicKey import RSA # <--- AGREGAR ESTO
import io


app = Flask(__name__)
app.secret_key = 'clave_secreta_para_sesion' # Necesario para mensajes flash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
crypto = CryptoManager()

# Crear tablas al iniciar
with app.app_context():
    db.create_all()

# --- RUTAS DEL FRONTEND ---

@app.route('/')
def index():
    """Página principal: Login y Registro"""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if User.query.filter_by(username=username).first():
        flash('El usuario ya existe.')
        return redirect(url_for('index'))

    # Generar llaves
    priv_pem, pub_pem = crypto.generate_user_keys()

    # AHORA (Encriptamos antes de guardar):
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_pw, public_key_pem=pub_pem.decode())
    db.session.add(new_user)
    db.session.commit()

    # Descargar llave privada automáticamente
    return send_file(
        io.BytesIO(priv_pem),
        mimetype='application/x-pem-file',
        as_attachment=True,
        download_name=f'{username}_private.key'
    )

@app.route('/voting_booth', methods=['GET', 'POST'])
def voting_booth():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        vote_content = request.form['vote']
        
        # 1. RECIBIR EL ARCHIVO DE LA LLAVE
        uploaded_file = request.files['key_file']
        if not uploaded_file:
            flash('Error: Debes subir tu archivo de llave privada.')
            return redirect(url_for('voting_booth'))

        # 2. AUTENTICACIÓN BÁSICA (Password)
        user = User.query.filter_by(username=username).first()
        
        # AHORA (Usamos la función de chequeo seguro):
        if not user or not check_password_hash(user.password, password):
            flash('Error: Credenciales incorrectas.')
            return redirect(url_for('voting_booth'))
        
        if user.has_voted:
            flash('Error: Usted YA ha votado.')
            return redirect(url_for('voting_booth'))

        # 3. VALIDACIÓN CRIPTOGRÁFICA (LA LLAVE PRIVADA)
        try:
            # Leemos el contenido del archivo subido
            key_data = uploaded_file.read()
            
            # Intentamos importar la llave privada con PyCryptodome
            user_private_key_obj = RSA.import_key(key_data)
            
            # Derivamos la pública de la privada que subió el usuario
            user_public_key_derived = user_private_key_obj.publickey().export_key().decode()
            
            # Comparamos con la pública que tenemos guardada en la Base de Datos
            # Limpiamos espacios por si acaso (.strip())
            stored_pub = user.public_key_pem.strip()
            uploaded_pub = user_public_key_derived.strip()

            if stored_pub != uploaded_pub:
                flash('ERROR CRÍTICO: Esta llave privada NO PERTENECE al usuario indicado.')
                return redirect(url_for('voting_booth'))

        except Exception as e:
            print(e) # Para ver el error en consola si pasa algo
            flash('Error: El archivo subido no es una llave válida o está corrupto.')
            return redirect(url_for('voting_booth'))

        # --- SI LLEGA AQUÍ, EL USUARIO ES QUIEN DICE SER (TIENE LA LLAVE) ---

        # LOGICA DE CEGADO (Igual que antes)
        n, e = crypto.get_admin_pub_params()
        blinded_val, r = crypto.blind_message(vote_content, n, e)

        # FIRMA CIEGA
        blinded_signature = crypto.sign_blinded(blinded_val)
        user.has_voted = True
        db.session.commit()

        # DESCEGADO Y DEPOSITO
        real_signature = crypto.unblind_signature(blinded_signature, r, n)
        new_vote = Vote(vote_content=vote_content, signature=str(real_signature))
        db.session.add(new_vote)
        db.session.commit()

        return render_template('success.html', signature=str(real_signature))

    return render_template('vote.html')

@app.route('/results')
def results():
    votes = Vote.query.all()

    # 1. Extraer solo los nombres de los candidatos de los votos
    vote_names = [v.vote_content for v in votes]

    # 2. Contar frecuencia (Ej: {'Partido Python': 5, 'Alianza Java': 3})
    vote_counts = Counter(vote_names)

    # 3. Separar en dos listas para la gráfica
    labels = list(vote_counts.keys())   # Nombres
    values = list(vote_counts.values()) # Cantidades

    return render_template('results.html', votes=votes, labels=labels, values=values)

@app.route('/credits')
def credits_page():
    return render_template('credits.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)