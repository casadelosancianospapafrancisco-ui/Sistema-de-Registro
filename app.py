from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps  # Para decorador login_required

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'  # Necesario para manejar sesiones

DB_PATH = "residentes.db"

# --- Crear base de datos si no existe ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viveres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_entrega TEXT,
                producto TEXT,
                cantidad INTEGER,
                fecha_vencimiento TEXT,
                bienes TEXT,
                utilidad TEXT
            )
        ''')
        conn.commit()

# --- Operaciones con la base de datos ---
def obtener_viveres():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM viveres")
        return cursor.fetchall()

def agregar_viveres(nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO viveres (nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad))
        conn.commit()

def obtener_por_id(viver_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM viveres WHERE id = ?", (viver_id,))
        return cursor.fetchone()

def actualizar_viveres(viver_id, nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE viveres
            SET nombre=?, fecha_entrega=?, producto=?, cantidad=?, fecha_vencimiento=?, bienes=?, utilidad=?
            WHERE id=?
        """, (nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad, viver_id))
        conn.commit()

def eliminar_viveres(viver_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM viveres WHERE id=?", (viver_id,))
        conn.commit()

# --- LOGIN / LOGOUT ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        if usuario == 'asilo' and contrasena == '121125':
            session['usuario'] = usuario
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# --- PROTECCIÓN DE RUTAS ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# --- RUTAS PRINCIPALES ---
@app.route('/')
@login_required
def inicio():
    registros = obtener_viveres()
    return render_template('inicio.html', viveres=registros)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nombre = request.form['nombre']
    fecha_entrega = request.form['fecha_entrega']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    fecha_vencimiento = request.form['fecha_vencimiento']
    bienes = request.form['bienes']
    utilidad = request.form['utilidad']
    agregar_viveres(nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad)
    return redirect('/')

@app.route('/editar/<int:viver_id>')
@login_required
def editar(viver_id):
    registro = obtener_por_id(viver_id)
    return render_template('editar.html', registro=registro)

@app.route('/actualizar/<int:viver_id>', methods=['POST'])
@login_required  # <-- protección añadida
def actualizar(viver_id):
    nombre = request.form['nombre']
    fecha_entrega = request.form['fecha_entrega']
    producto = request.form['producto']
    cantidad = request.form['cantidad']
    fecha_vencimiento = request.form['fecha_vencimiento']
    bienes = request.form['bienes']
    utilidad = request.form['utilidad']
    actualizar_viveres(viver_id, nombre, fecha_entrega, producto, cantidad, fecha_vencimiento, bienes, utilidad)
    return redirect('/')

@app.route('/eliminar/<int:viver_id>')
@login_required
def eliminar(viver_id):
    eliminar_viveres(viver_id)
    return redirect('/')

# --- INICIALIZAR DB ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
