# usuarios.py
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from flask_bcrypt import Bcrypt
from app.models.modelo_usuarios import (
    obtener_usuario_por_email,
    verificar_persona_existente,
    verificar_correo_existente,
    insertar_persona,
    insertar_usuario,
    obtener_datos_usuario
)

usuarios_bp = Blueprint('usuarios_bp', __name__)
bcrypt = Bcrypt()

@usuarios_bp.route('/iniciar-sesion', methods=['GET', 'POST'])
def iniciarSesion():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['contrasena']
        connection = current_app.connection

        try:
            result = obtener_usuario_por_email(connection, email)
            if result and bcrypt.check_password_hash(result['Contraseña'], password):
                session['email'] = email
                session['user_id'] = result['Persona_num_identificacion']
                session['nombre'] = result['Nombre']
                session['apellido'] = result['Apellido']
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('main_bp.Home'))
            else:
                flash('Email o contraseña incorrectos', 'error')
        except Exception as e:
            flash('Error en el servidor. Intenta nuevamente.', 'error')
            print(f"Error en iniciar sesión: {str(e)}")

    return render_template('usuarios/iniciar-sesion.html')


@usuarios_bp.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'GET':
        return render_template('usuarios/registrarse.html')

    connection = current_app.connection
    num_identificacion = request.form['num_identificacion']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    telefono = request.form.get('telefono', '')
    password = request.form['password']
    tipo_documento = request.form['tipo_documento']

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        if verificar_persona_existente(connection, num_identificacion):
            flash('Ya existe una persona registrada con ese número de identificación', 'error')
            return render_template('usuarios/registrarse.html')

        if verificar_correo_existente(connection, correo):
            flash('Ya existe una cuenta con ese correo electrónico', 'error')
            return render_template('usuarios/registrarse.html')

        insertar_persona(connection, num_identificacion, nombre, apellido, correo, telefono, tipo_documento)
        insertar_usuario(connection, hashed_password, num_identificacion, tipo_documento)

        connection.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('usuarios_bp.iniciarSesion'))

    except Exception as e:
        connection.rollback()
        flash('Error al registrar usuario. Intenta nuevamente.', 'error')
        print(f"Error en registro: {str(e)}")
        return render_template('usuarios/registrarse.html')


@usuarios_bp.route('/cerrar-sesion')
def cerrarSesion():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('usuarios_bp.iniciarSesion'))


@usuarios_bp.route('/perfil')
def perfil():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a tu perfil', 'error')
        return redirect(url_for('usuarios_bp.iniciarSesion'))

    connection = current_app.connection
    try:
        usuario = obtener_datos_usuario(connection, session['user_id'])
        if usuario:
            return render_template('usuarios/perfil.html', usuario=usuario)
        else:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('usuarios_bp.iniciarSesion'))

    except Exception as e:
        flash('Error al cargar perfil', 'error')
        print(f"Error en perfil: {str(e)}")
        return redirect(url_for('main_bp.Home'))


# Decorador de autenticación
def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('usuarios_bp.iniciarSesion'))
        return f(*args, **kwargs)
    return decorated_function