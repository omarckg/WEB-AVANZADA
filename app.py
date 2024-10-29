from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from db_config import get_db_connection
import bcrypt
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta' 

# Credenciales del administrador

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "maestro"  

@app.route('/')  # Define la ruta principal
def home():
    return render_template('index.html')  
# Renderiza la plantilla de inicio
@app.route('/pregrados')  # Define la ruta para la página de Pregrados
def pregrados():
    return render_template('Pregrados.html') 
@app.route('/nosotros')  # Define la ruta para la página "Nosotros"
def nosotros():
    return render_template('Nosotros.html')

@app.route('/ofertas')  # Define la ruta para la página de Ofertas Académicas
def ofertas():
    return render_template('Ofertas.html') 

@app.route('/docentes')  # Define la ruta para la página de Ofertas Académicas
def docentes():
    return render_template('Do.html')# Renderiza la plantilla Ofertas.html# Renderiza la plantilla Nosotros.html

@app.route('/inscribete')  # Define la ruta para la página de Ofertas Académicas
def inscribete():
    return render_template('inscribete.html')

@app.route('/bienestar')  # Define la ruta para la página de Bienestar
def bienestar():
    return render_template('bienestar.html')
@app.route('/BaseDatos')  # Define la ruta para la página de Base de Datos
def BaseDatos():
    return render_template('BaseDatos.html')  # Renderiza la plantilla BaseDatos.html# Renderiza la plantilla bienestar.html

@app.route('/Biblioteca')  # Define la ruta para la página de Biblioteca
def Biblioteca():
    return render_template('Biblioteca.html')  # Renderiza la plantilla Biblioteca.html
@app.route('/login', methods=['GET', 'POST'])  # Define la ruta para el inicio de sesión
def login():
    if request.method == 'GET':
        return render_template('login.html')  # Renderiza la página de inicio de sesión
    username = request.form['username']
    password = request.form['password']

    # Verifica si el usuario es el administrador
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['rol'] = 'admin'  # Almacena el rol en la sesión
        # Marca al usuario como autenticado
        return redirect(url_for('admin'))  # Redirige a la página de administración

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):  # Verifica la contraseña
        session['logged_in'] = True  # Almacenar el estado de sesión
        session['username'] = username  # Almacena el nombre de usuario en la sesión
        session['user_id'] = user[0]
        session['rol'] = user[3] # Almacena el ID del usuario en la sesión
        if user[3] == 'estudiante':  # Verificar el rol del usuario
            return redirect(url_for('estudiante'))  # Redirigir a la función estudiante
        elif user[3] == 'admin':  # Verificar si el rol es admin
            return redirect(url_for('admin'))  # Redirigir a la función perfil_admin
        elif user[3] == 'profesor':  # Verificar si el rol es profesor
            return redirect(url_for('profesor'))  # Redirigir a la función profesor
    else:
        return "Usuario o contraseña incorrectos"

@app.route('/index')
def index():
    return render_template('index.html')  # Renderizar la plantilla index.html

@app.route('/estudiante')
def estudiante():
    if not session.get('logged_in'):  # Verificar si el usuario está autenticado
        return redirect(url_for('home'))  # Redirigir a la página de inicio si no está autenticado
    return render_template('estudiante.html')  # Renderizar la página de estudiante

@app.route('/register', methods=['POST'])  # Define la ruta para registrar un nuevo usuario
def register():
    username = request.form['username']
    email = request.form['email']  # Obtener el correo electrónico
    documento_identidad = request.form['documento_identidad']  # Obtener el documento de identidad
    tipo_documento = request.form['tipo_documento']  # Obtener el tipo de documento
    password = request.form['password']
    rol = request.form['rol']  # Obtener el rol del formulario
    semestre = request.form.get('semestre')  # Obtener el semestre del formulario, puede ser None si no se selecciona

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Inserta en la tabla 'users' incluyendo el rol, semestre, documento de identidad y tipo de documento
        cursor.execute("INSERT INTO users (username, email, documento_identidad, tipo_documento, password, rol, semestre) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (username, email, documento_identidad, tipo_documento, hashed_password, rol, semestre))
        connection.commit()

        # Almacenar el estado de sesión para el nuevo usuario
        session['logged_in'] = True  # Marcar al usuario como autenticado
        return redirect(url_for('admin'))  # Redirigir a la página de administración después del registro exitoso
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        connection.close()

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('registrar.html')  # Renderizar la plantilla registrar.html

@app.route('/logout')  # Define la ruta para cerrar sesión
def logout():
    session.pop('logged_in', None)  # Elimina el estado de sesión
    return redirect(url_for('login'))  # Redirige a la página de inicio

@app.route('/users', methods=['GET'])
def list_users():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, username, rol FROM users")  # Selecciona el ID, nombre de usuario y rol
        users = cursor.fetchall()
        print(users)  # Para verificar que hay usuarios
        if not users:
            print("No hay usuarios registrados.")
    except Exception as e:  # Corregir la indentación aquí
        return f"Error al obtener usuarios: {e}"
    finally:
        cursor.close()
        connection.close()
    
    return render_template('eliminar.html', users=users)  # Renderizar la plantilla con los usuarios

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        return redirect(url_for('list_users'))  # Redirigir a la lista de usuarios después de eliminar
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        cursor.close()
        connection.close()

@app.route('/eliminar')
def eliminar():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, username, rol FROM users")  # Selecciona el ID, nombre de usuario y rol
        users = cursor.fetchall()  # Obtiene todos los usuarios
    except Exception as e:
        return f"Error al obtener usuarios: {e}"
    finally:
        cursor.close()
        connection.close()
    
    return render_template('eliminar.html', users=users)  # Renderizar la plantilla con los usuarios

@app.route('/profesor')  # Nueva ruta para el profesor
def profesor():
    if not session.get('logged_in'):  # Verificar si el usuario está autenticado
        return redirect(url_for('home'))  # Redirigir a la página de inicio si no está autenticado
    return render_template('profesor.html')  # Renderizar la página de profesor

@app.route('/admin')  # Define la ruta para la página del administrador
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    # Obtener la información del administrador desde la base de datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username, id, rol, password FROM users WHERE rol = %s", ('admin',))
    admin = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if admin:
        admin_info = {
            'nombre': admin[0],
            'id': admin[1],
            'rol': admin[2],
            'contraseña': admin[3]
        }
        return render_template('admin.html', admin=admin_info)
    else:
        return "Administrador no encontrado"

@app.route('/perfil_admin')  # Define la ruta para el perfil del administrador
def perfil_admin():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redirige a la página de inicio si no está autenticado

    # Obtener la información del administrador desde la sesión
    username = session.get('username')
    user_id = session.get('user_id')
    rol = session.get('rol')

    # Puedes obtener más información de la base de datos si es necesario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT email, documento_identidad, tipo_documento FROM users WHERE id = %s", (user_id,))
    admin_info = cursor.fetchone()
    cursor.close()
    connection.close()

    if admin_info:
        admin_data = {
            'nombre': username,  # Usar el nombre de usuario almacenado en la sesión
            'id': user_id,
            'rol': rol,  # Asegúrate de que el rol se incluya aquí
            'email': admin_info[0],
            'documento_identidad': admin_info[1],
            'tipo_documento': admin_info[2]
        }
        return render_template('Perfiladmin.html', admin=admin_data)
    else:
        return "Perfil del administrador no encontrado"

@app.route('/perfil_estudiante')
def perfil_estudiante():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redirige a la página de inicio si no está autenticado

    # Obtener la información del estudiante desde la sesión
    username = session.get('username')
    user_id = session.get('user_id')
    rol = session.get('rol')

    # Puedes obtener más información de la base de datos si es necesario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT email, documento_identidad, tipo_documento FROM users WHERE id = %s", (user_id,))
    estudiante_info = cursor.fetchone()
    cursor.close()
    connection.close()

    if estudiante_info:
        estudiante_data = {
            'username': username,
            'id': user_id,
            'rol': rol,
            'email': estudiante_info[0],
            'documento_identidad': estudiante_info[1],
            'tipo_documento': estudiante_info[2]
        }
        return render_template('PerfilEstudiante.html', estudiante=estudiante_data)
    else:
        return "Información del estudiante no encontrada"

@app.route('/perfil_profesor')
def perfil_profesor():
    if not session.get('logged_in'):
        return redirect(url_for('home'))  # Redirige a la página de inicio si no está autenticado

    # Obtener la información del profesor desde la sesión
    user_id = session.get('user_id')
    username = session.get('username')
    rol = session.get('rol')

    # Puedes obtener más información de la base de datos si es necesario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT email, documento_identidad, tipo_documento FROM users WHERE id = %s", (user_id,))
    profesor_info = cursor.fetchone()
    cursor.close()
    connection.close()

    if profesor_info:
        profesor_data = {
            'nombre': username,  # Usar el nombre de usuario almacenado en la sesión
            'id': user_id,
            'rol': rol,  # Asegúrate de que el rol se incluya aquí
            'email': profesor_info[0],
            'documento_identidad': profesor_info[1],
            'tipo_documento': profesor_info[2]
        }
        return render_template('Perfilprofesor.html', profesor=profesor_data)
    else:
        return "Información del profesor no encontrada"

@app.route('/asignaturas')
def asignaturas():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT a.id, a.nombre, u.username 
        FROM asignaturas a 
        JOIN users u ON a.profesor_id = u.id
    """)
    asignaturas = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('Asignatura.html', asignaturas=asignaturas)

@app.route('/agregar_asignatura', methods=['GET', 'POST'])
def agregar_asignatura():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    if request.method == 'POST':
        nombre_asignatura = request.form['nombre_asignatura']
        nombre_profesor = request.form['nombre_profesor']
        
        # Verificar si el profesor existe en la base de datos
        cursor.execute("SELECT id FROM users WHERE username = %s AND rol = 'profesor'", (nombre_profesor,))
        profesor = cursor.fetchone()
        
        if profesor:
            profesor_id = profesor[0]
            cursor.execute("INSERT INTO asignaturas (nombre, profesor_id) VALUES (%s, %s)", (nombre_asignatura, profesor_id))
            connection.commit()
        else:
            cursor.close()
            connection.close()
            return "Profesor no encontrado"
        
        cursor.close()
        connection.close()
        return redirect(url_for('asignaturas'))
    
    # Obtener la lista de profesores
    cursor.execute("SELECT username FROM users WHERE rol = 'profesor'")
    profesores = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('Agregarasignatura.html', profesores=profesores)

@app.route('/asignar_notas', methods=['GET', 'POST'])
def asignar_notas():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    if request.method == 'POST':
        estudiante_id = request.form['estudiante_id']
        asignatura_id = request.form['asignatura_id']
        nota = request.form['nota']
        
        # Insertar la nota en la base de datos
        cursor.execute("INSERT INTO notas (estudiante_id, asignatura_id, nota) VALUES (%s, %s, %s)", (estudiante_id, asignatura_id, nota))
        connection.commit()
        
        cursor.close()
        connection.close()
        return redirect(url_for('notas'))  # Redirigir a la página de notas después de asignar una nota
    
    # Obtener la lista de estudiantes y asignaturas, incluyendo el semestre
    cursor.execute("SELECT id, username, semestre FROM users WHERE rol = 'estudiante'")
    estudiantes = cursor.fetchall()
    
    cursor.execute("SELECT id, nombre FROM asignaturas")
    asignaturas = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('Asignarnotas.html', estudiantes=estudiantes, asignaturas=asignaturas)

@app.route('/notas')
def notas():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT n.id, u.username AS estudiante, a.nombre AS asignatura, n.nota, u.semestre
        FROM notas n
        JOIN users u ON n.estudiante_id = u.id
        JOIN asignaturas a ON n.asignatura_id = a.id
    """)
    notas = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('Notas.html', notas=notas)

@app.route('/asignaturas_estudiante')
def asignaturas_estudiante():
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    
    username = session.get('username')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(""" 
            SELECT a.nombre, p.username AS profesor
            FROM asignaturas a
            JOIN users p ON a.profesor_id = p.id
            JOIN notas n ON a.id = n.asignatura_id
            JOIN users e ON n.estudiante_id = e.id
            WHERE e.username = %s
        """, (username,))
        asignaturas = cursor.fetchall()  # Asegúrate de que esta variable se llame 'asignaturas'
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        asignaturas = []  # Asegúrate de que asignaturas tenga un valor por defecto
    finally:
        cursor.close()
        connection.close()
    
    return render_template('Asignaturaestudiante.html', asignaturas=asignaturas)  # Asegúrate de pasar 'asignaturas'

@app.route('/notas_estudiante')
def notas_estudiante():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    username = session.get('username')  # Obtener el nombre de usuario del estudiante en sesión
    connection = get_db_connection()
    cursor = connection.cursor()

    # Modificar la consulta para obtener las notas del estudiante actual
    cursor.execute("""
        SELECT n.id, a.nombre AS asignatura, n.nota
        FROM notas n
        JOIN asignaturas a ON n.asignatura_id = a.id
        JOIN users u ON n.estudiante_id = u.id
        WHERE u.username = %s
    """, (username,))
    notas = cursor.fetchall()

    # Verifica si se obtuvieron notas
    print(f"Notas obtenidas: {notas}")  # Para depuración

    # Calcular el promedio de las notas
    if notas:
        total_notas = sum(nota[2] for nota in notas)  # Sumar las notas
        promedio = total_notas / len(notas)  # Calcular el promedio
    else:
        promedio = 0  # Si no hay notas, el promedio es 0

    cursor.close()
    connection.close()

    return render_template('Notasestudiante.html', notas=notas, promedio=promedio)

@app.route('/buscar_asignaturas', methods=['GET'])
def buscar_asignaturas():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Obtener las asignaturas
    cursor.execute("SELECT id, nombre FROM asignaturas")  # Cambia según tu estructura de base de datos
    asignaturas = cursor.fetchall()
    
    # Obtener los profesores
    cursor.execute("SELECT id, username FROM users WHERE rol = 'profesor'")  # Cambia según tu estructura de base de datos
    profesores = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('Buscar.html', asignaturas=asignaturas, profesores=profesores)

@app.route('/mostrar_asignaturas', methods=['POST'])
def mostrar_asignaturas():
    asignatura_id = request.form['asignatura']  # Obtener el ID de la asignatura seleccionada

    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Obtener la información de la asignatura y el profesor
    cursor.execute("""
        SELECT a.nombre, p.username 
        FROM asignaturas a 
        JOIN users p ON a.profesor_id = p.id 
        WHERE a.id = %s
    """, (asignatura_id,))
    asignatura = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if asignatura:
        return render_template('Asignaturaestudiante.html', asignaturas=[asignatura])  # Pasar la información a la plantilla
    else:
        return "Asignatura no encontrada"

@app.route('/buscar_notas', methods=['GET', 'POST'])
def buscar_notas():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Obtener las asignaturas
    cursor.execute("SELECT id, nombre FROM asignaturas")
    asignaturas = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('buscarnotas.html', asignaturas=asignaturas)

@app.route('/mostrar_notas', methods=['POST'])
def mostrar_notas():
    asignatura_id = request.form['asignatura']  # Obtener el ID de la asignatura seleccionada

    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Obtener las notas de la asignatura seleccionada
    cursor.execute("""
        SELECT n.id, u.username AS estudiante, n.nota
        FROM notas n
        JOIN users u ON n.estudiante_id = u.id
        WHERE n.asignatura_id = %s
    """, (asignatura_id,))
    notas = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('Notasestudiante.html', notas=notas)



if __name__ == '__main__':
    app.run(debug=True)
