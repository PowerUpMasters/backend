from database import db

class Docente(db.Model):
    __tablename__ = 'docentes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    cursos = db.relationship('Curso', backref='docente', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "documento": self.documento,
            "correo": self.correo
        }

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    duracion_semanas = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_inicio = db.Column(db.String(50), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey('docentes.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "duracion_semanas": self.duracion_semanas,
            "precio": self.precio,
            "fecha_inicio": self.fecha_inicio,
            "docente": self.docente.to_dict() if self.docente else None
        }
