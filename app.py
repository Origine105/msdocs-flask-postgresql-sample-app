import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# Configuración de entorno
if 'WEBSITE_HOSTNAME' not in os.environ:
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Carpeta para guardar las imágenes subidas
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista de extensiones permitidas (se incluye bmp)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from models import ImageRecord  # El modelo debe incluir los campos 'entrada' y 'salida'

@app.route('/', methods=['GET'])
def viewer():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Puedes ajustar según tus necesidades
    pagination = ImageRecord.query.order_by(ImageRecord.timestamp.desc()).paginate(page=page, per_page=per_page)
    records = pagination.items
    params = {k: v for k, v in request.args.items() if k != 'page'}
    return render_template('index.html', records=records, pagination=pagination, params=params)

# Endpoint API para recibir la subida de imágenes (multipart/form-data)
@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def api_upload():
    # Recuperar metadatos del formulario
    filename_field = request.form.get('filename')  # Campo opcional para el nombre del registro
    username = request.form.get('username')
    pixels_red = int(request.form.get('pixels_red', 0))
    pixels_green = int(request.form.get('pixels_green', 0))
    pixels_blue = int(request.form.get('pixels_blue', 0))
    
    # Recuperar los archivos enviados
    entrada_file = request.files.get('entrada_file')
    salida_file = request.files.get('salida_file')
    
    # Validar existencia de ambos archivos
    if not entrada_file or not salida_file:
        return jsonify({'status': 'error', 'message': 'No se enviaron ambos archivos'}), 400

    # Validar extensiones (se incluye 'bmp')
    if not (allowed_file(entrada_file.filename) and allowed_file(salida_file.filename)):
        return jsonify({'status': 'error', 'message': 'Tipo de archivo no permitido'}), 400

    # Limpiar nombres de archivo
    entrada_filename = secure_filename(entrada_file.filename)
    salida_filename = secure_filename(salida_file.filename)

    # Guardar archivos en UPLOAD_FOLDER
    entrada_path = os.path.join(app.config['UPLOAD_FOLDER'], entrada_filename)
    salida_path = os.path.join(app.config['UPLOAD_FOLDER'], salida_filename)
    entrada_file.save(entrada_path)
    salida_file.save(salida_path)

    # Si no se suministra filename, se usa el de entrada
    if not filename_field:
        filename_field = entrada_filename

    # Crear el registro en la base de datos con rutas relativas (por ejemplo, "uploads/entrada.bmp")
    record = ImageRecord(
        filename=filename_field,
        pixels_red=pixels_red,
        pixels_green=pixels_green,
        pixels_blue=pixels_blue,
        username=username,
        timestamp=datetime.now(timezone.utc),
        entrada=os.path.join('uploads', entrada_filename),
        salida=os.path.join('uploads', salida_filename)
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'status': 'ok', 'id': record.id}), 201

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
