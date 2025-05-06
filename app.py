import os
import base64
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

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
    SQLALCHEMY_DATABASE_URI    = app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

db     = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import ImageRecord

@app.route('/', methods=['GET'])
def viewer():
    page     = request.args.get('page', 1, type=int)
    per_page = 10  # Puedes ajustar cuántos registros quieres por página
    pagination = ImageRecord.query \
        .order_by(ImageRecord.timestamp.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    params  = {k: v for k, v in request.args.items() if k != 'page'}
    return render_template('index.html', records=records, pagination=pagination, params=params)

@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def api_upload():
    """
    Espera JSON con:
      - filename, pixels_red, pixels_green, pixels_blue, username,
      - entrada_b64 : BMP de entrada codificado en Base64
      - salida_b64  : BMP de salida  codificado en Base64
    Decodifica y guarda ambos .bmp en static/, y registra el ImageRecord con entrada/salida.
    """
    data = request.get_json(force=True)
    filename    = data.get('filename')
    entrada_b64 = data.get('entrada_b64')
    salida_b64  = data.get('salida_b64')

    # Validación mínima
    if not all([filename, entrada_b64, salida_b64]):
        return jsonify({'error': 'Faltan filename y/o los campos Base64'}), 400

    # Decodificar Base64 a bytes
    try:
        bytes_in  = base64.b64decode(entrada_b64)
        bytes_out = base64.b64decode(salida_b64)
    except Exception as e:
        return jsonify({'error': f'Error decodificando Base64: {e}'}), 400

    # Generar nombres únicos para los ficheros
    ts       = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    in_name  = f"{filename}_in_{ts}.bmp"
    out_name = f"{filename}_out_{ts}.bmp"

    # Guardar los BMP en el directorio static/
    in_path  = os.path.join(app.static_folder, in_name)
    out_path = os.path.join(app.static_folder, out_name)
    with open(in_path,  'wb') as f: f.write(bytes_in)
    with open(out_path, 'wb') as f: f.write(bytes_out)

    # Crear y guardar el registro con las rutas de las imágenes
    record = ImageRecord(
        filename    = filename,
        pixels_red   = data['pixels_red'],
        pixels_green = data['pixels_green'],
        pixels_blue  = data['pixels_blue'],
        username    = data['username'],
        timestamp   = datetime.now(timezone.utc),
        entrada     = in_name,
        salida      = out_name
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({'status': 'ok', 'id': record.id}), 201

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__ == '__main__':
    app.run()
