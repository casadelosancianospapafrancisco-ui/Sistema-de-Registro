from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = "cambia_esta_clave_por_una_segura"  # <- cámbiala antes de entregar

# ---------- Helpers DB ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Tabla ancianos
    c.execute('''
        CREATE TABLE IF NOT EXISTS ancianos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha_ingreso TEXT NOT NULL,
            edad INTEGER,
            observaciones TEXT
        )
    ''')
    # Tabla viveres
    c.execute('''
        CREATE TABLE IF NOT EXISTS viveres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_donante TEXT,
            fecha_ingreso TEXT,
            producto TEXT,
            cantidad INTEGER,
            fecha_vencimiento TEXT,
            saldo INTEGER,
            bienes TEXT,
            cantidad_usada INTEGER,
            utilidad TEXT,
            buen_estado INTEGER DEFAULT 0,
            mal_estado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar DB al arrancar (si no existe)
init_db()

# ---------- Seguridad (login) ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# Credenciales (fijas) - cámbialas o implementa usuarios en DB
VALID_USERS = {
    "asilo": "121125"
}

# ---------- Rutas de auth ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        if usuario in VALID_USERS and VALID_USERS[usuario] == contrasena:
            session['usuario'] = usuario
            flash("Inicio de sesión correcto", "success")
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash("Sesión cerrada", "info")
    return redirect(url_for('login'))

# ---------- Página principal (menú) ----------
@app.route('/')
@login_required
def home():
    return render_template('inicio.html')

# =======================
# ===== Ancianos CRUD ===
# =======================
@app.route('/ancianos')
@login_required
def ancianos_list():
    conn = get_db_connection()
    ancianos = conn.execute("SELECT * FROM ancianos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('ancianos_list.html', ancianos=ancianos)

@app.route('/ancianos/agregar', methods=['GET', 'POST'])
@login_required
def ancianos_add():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        fecha_ingreso = request.form['fecha_ingreso']
        edad = request.form.get('edad') or None
        observaciones = request.form.get('observaciones') or None

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO ancianos (nombre, fecha_ingreso, edad, observaciones) VALUES (?, ?, ?, ?)",
            (nombre, fecha_ingreso, edad, observaciones)
        )
        conn.commit()
        conn.close()
        flash("Anciano registrado correctamente", "success")
        return redirect(url_for('ancianos_list'))
    return render_template('ancianos_form.html', action="Agregar", anciano=None)

@app.route('/ancianos/editar/<int:anc_id>', methods=['GET', 'POST'])
@login_required
def ancianos_edit(anc_id):
    conn = get_db_connection()
    anc = conn.execute("SELECT * FROM ancianos WHERE id = ?", (anc_id,)).fetchone()
    conn.close()
    if not anc:
        flash("Registro no encontrado", "error")
        return redirect(url_for('ancianos_list'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        fecha_ingreso = request.form['fecha_ingreso']
        edad = request.form.get('edad') or None
        observaciones = request.form.get('observaciones') or None

        conn = get_db_connection()
        conn.execute(
            "UPDATE ancianos SET nombre=?, fecha_ingreso=?, edad=?, observaciones=? WHERE id=?",
            (nombre, fecha_ingreso, edad, observaciones, anc_id)
        )
        conn.commit()
        conn.close()
        flash("Registro actualizado", "success")
        return redirect(url_for('ancianos_list'))

    return render_template('ancianos_form.html', action="Editar", anciano=anc)

@app.route('/ancianos/eliminar/<int:anc_id>', methods=['POST'])
@login_required
def ancianos_delete(anc_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM ancianos WHERE id = ?", (anc_id,))
    conn.commit()
    conn.close()
    flash("Registro eliminado", "info")
    return redirect(url_for('ancianos_list'))

# =======================
# ===== VÍVERES CRUD ====
# =======================
@app.route('/viveres')
@login_required
def viveres_list():
    conn = get_db_connection()
    datos = conn.execute("SELECT * FROM viveres ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('viveres_list.html', datos=datos)

@app.route('/viveres/agregar', methods=['GET', 'POST'])
@login_required
def viveres_add():
    if request.method == 'POST':
        nombre_donante = request.form.get('nombre_donante') or None
        fecha_ingreso = request.form.get('fecha_ingreso') or None
        producto = request.form.get('producto') or None
        cantidad = int(request.form.get('cantidad') or 0)
        fecha_vencimiento = request.form.get('fecha_vencimiento') or None
        bienes = request.form.get('bienes') or None
        buen_estado = 1 if request.form.get('buen_estado') == '1' else 0
        mal_estado = 1 if request.form.get('mal_estado') == '1' else 0
        saldo = cantidad  # inicialmente el saldo es la cantidad ingresada

        conn = get_db_connection()
        conn.execute(
            '''INSERT INTO viveres
               (nombre_donante, fecha_ingreso, producto, cantidad, fecha_vencimiento, saldo, bienes, buen_estado, mal_estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (nombre_donante, fecha_ingreso, producto, cantidad, fecha_vencimiento, saldo, bienes, buen_estado, mal_estado)
        )
        conn.commit()
        conn.close()
        flash("Registro de víveres guardado", "success")
        return redirect(url_for('viveres_list'))
    return render_template('viveres_form.html', action="Agregar", registro=None)

@app.route('/viveres/editar/<int:vid>', methods=['GET', 'POST'])
@login_required
def viveres_edit(vid):
    conn = get_db_connection()
    reg = conn.execute("SELECT * FROM viveres WHERE id = ?", (vid,)).fetchone()
    conn.close()
    if not reg:
        flash("Registro no encontrado", "error")
        return redirect(url_for('viveres_list'))

    if request.method == 'POST':
        nombre_donante = request.form.get('nombre_donante') or None
        fecha_ingreso = request.form.get('fecha_ingreso') or None
        producto = request.form.get('producto') or None
        cantidad = int(request.form.get('cantidad') or 0)
        fecha_vencimiento = request.form.get('fecha_vencimiento') or None
        bienes = request.form.get('bienes') or None
        buen_estado = 1 if request.form.get('buen_estado') == '1' else 0
        mal_estado = 1 if request.form.get('mal_estado') == '1' else 0
        saldo = cantidad  # recomputar saldo si cambias cantidad

        conn = get_db_connection()
        conn.execute(
            '''UPDATE viveres
               SET nombre_donante=?, fecha_ingreso=?, producto=?, cantidad=?, fecha_vencimiento=?, saldo=?, bienes=?, buen_estado=?, mal_estado=?
               WHERE id=?''',
            (nombre_donante, fecha_ingreso, producto, cantidad, fecha_vencimiento, saldo, bienes, buen_estado, mal_estado, vid)
        )
        conn.commit()
        conn.close()
        flash("Registro actualizado", "success")
        return redirect(url_for('viveres_list'))

    return render_template('viveres_form.html', action="Editar", registro=reg)

@app.route('/viveres/eliminar/<int:vid>', methods=['POST'])
@login_required
def viveres_delete(vid):
    conn = get_db_connection()
    conn.execute("DELETE FROM viveres WHERE id = ?", (vid,))
    conn.commit()
    conn.close()
    flash("Registro eliminado", "info")
    return redirect(url_for('viveres_list'))

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
