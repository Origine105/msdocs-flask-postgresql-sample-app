import os
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
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import ImageRecord

@app.route('/', methods=['GET'])
def viewer():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Puedes ajustar cuántos registros quieres por página
    pagination = ImageRecord.query.order_by(ImageRecord.timestamp.desc()).paginate(page=page, per_page=per_page)
    records = pagination.items
    params = {k: v for k, v in request.args.items() if k != 'page'}
    return render_template('index.html', records=records, pagination=pagination, params=params)

@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def api_upload():
    # Se espera JSON con campos: filename, pixels_red, pixels_green, pixels_blue, username, (opcional) entrada, salida.
    data = request.get_json(force=True)
    record = ImageRecord(
        filename=data['filename'],
        pixels_red=data['pixels_red'],
        pixels_green=data['pixels_green'],
        pixels_blue=data['pixels_blue'],
        username=data['username'],
        timestamp=datetime.now(timezone.utc),
        entrada=data.get('entrada'),  # ruta de imagen de entrada (relativa a static/)
        salida=data.get('salida')       # ruta de imagen de salida (relativa a static/)
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
