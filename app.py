from flask import Flask, jsonify, request, render_template
from database import db
from models import Docente, Curso

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cesde_cursos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/docentes', methods=['GET'])
def listar_docentes():
    docentes = Docente.query.all()
    return jsonify([d.to_dict() for d in docentes]), 200

@app.route('/api/docentes', methods=['POST'])
def crear_docente():
    data = request.get_json()
    if not data or not all(k in data for k in ('nombre', 'documento', 'correo')):
        return jsonify({"error": "Faltan campos obligatorios: nombre, documento, correo"}), 400
    
    if Docente.query.filter_by(documento=data['documento']).first():
        return jsonify({"error": "El docente con este número de documento ya existe"}), 400

    nuevo_docente = Docente(
        nombre=data['nombre'],
        documento=data['documento'],
        correo=data['correo']
    )
    db.session.add(nuevo_docente)
    db.session.commit()
    return jsonify(nuevo_docente.to_dict()), 201

@app.route('/api/cursos', methods=['GET'])
def listar_cursos():
    cursos = Curso.query.all()
    return jsonify([c.to_dict() for c in cursos]), 200

@app.route('/api/cursos', methods=['POST'])
def crear_curso():
    data = request.get_json()
    required = ('nombre', 'descripcion', 'duracion_semanas', 'precio', 'fecha_inicio', 'docente_id')
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    docente = Docente.query.get(data['docente_id'])
    if not docente:
        return jsonify({"error": "El docente especificado no existe"}), 404

    nuevo_curso = Curso(
        nombre=data['nombre'],
        descripcion=data['descripcion'],
        duracion_semanas=int(data['duracion_semanas']),
        precio=float(data['precio']),
        fecha_inicio=data['fecha_inicio'],
        docente_id=docente.id
    )
    db.session.add(nuevo_curso)
    db.session.commit()
    return jsonify(nuevo_curso.to_dict()), 201

@app.route('/api/cursos/<int:id>', methods=['PUT'])
def actualizar_curso(id):
    curso = Curso.query.get_or_404(id)
    data = request.get_json()

    curso.nombre = data.get('nombre', curso.nombre)
    curso.descripcion = data.get('descripcion', curso.descripcion)
    curso.duracion_semanas = int(data.get('duracion_semanas', curso.duracion_semanas))
    curso.precio = float(data.get('precio', curso.precio))
    curso.fecha_inicio = data.get('fecha_inicio', curso.fecha_inicio)
    
    if 'docente_id' in data:
        docente = Docente.query.get(data['docente_id'])
        if not docente:
            return jsonify({"error": "El docente especificado no existe"}), 404
        curso.docente_id = docente.id

    db.session.commit()
    return jsonify(curso.to_dict()), 200

@app.route('/api/cursos/<int:id>', methods=['DELETE'])
def eliminar_curso(id):
    curso = Curso.query.get_or_404(id)
    db.session.delete(curso)
    db.session.commit()
    return '', 204

@app.route('/api/cursos/filtrar/nombre', methods=['GET'])
def filtrar_por_nombre():
    nombre = request.args.get('nombre', '')
    cursos = Curso.query.filter(Curso.nombre.ilike(f'%{nombre}%')).all()
    return jsonify([c.to_dict() for c in cursos]), 200

@app.route('/api/cursos/filtrar/precio', methods=['GET'])
def filtrar_por_precio():
    try:
        precio_max = float(request.args.get('max', 0))
    except ValueError:
        return jsonify({"error": "El parámetro 'max' debe ser un número válido"}), 400
    
    cursos = Curso.query.filter(Curso.precio <= precio_max).all()
    return jsonify([c.to_dict() for c in cursos]), 200

@app.route('/api/cursos/filtrar/docente', methods=['GET'])
def filtrar_por_docente_documento():
    documento = request.args.get('documento', '')
    cursos = Curso.query.join(Docente).filter(Docente.documento == documento).all()
    return jsonify([c.to_dict() for c in cursos]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
