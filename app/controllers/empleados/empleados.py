from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from flask_bcrypt import Bcrypt
from app.models import modelo_empleados as modelo

empleados_bp = Blueprint('empleados', __name__, url_prefix='/empleados')
bcrypt = Bcrypt()

@empleados_bp.route('/')
def mostrar_empleados():
    return render_template('Empleados/empleados.html')

@empleados_bp.route('/consultar_empleado', methods=['GET', 'POST'])
def consultar_empleado():
    connection = current_app.connection
    usuarios = []
    usuario_encontrado = None
    mensaje = None

    try:
        usuarios = modelo.obtener_usuarios(connection)
    except Exception as e:
        flash('Error al cargar usuarios', 'error')
        print(f"Error al cargar usuarios: {str(e)}")

    if request.method == 'GET':
        id_usuario = request.args.get('id_usuario')
        if id_usuario:
            try:
                usuario_encontrado = modelo.buscar_empleado_por_id(connection, id_usuario)
                mensaje = 'Empleado encontrado exitosamente' if usuario_encontrado else 'No se encontró el empleado especificado'
            except Exception as e:
                mensaje = 'Error al buscar empleado. Intenta nuevamente.'
                print(f"Error en búsqueda: {str(e)}")
        return render_template('Empleados/consultar_empleado.html', usuarios=usuarios, usuario_encontrado=usuario_encontrado, mensaje=mensaje)

    if request.method == 'POST':
        criterio = request.form.get('criterio_busqueda')
        valor = request.form.get('valor_busqueda', '').strip()
        id_usuario_dropdown = request.form.get('id_usuario')

        try:
            if id_usuario_dropdown:
                usuario_encontrado = modelo.buscar_empleado_por_id(connection, id_usuario_dropdown)
                mensaje = 'Empleado encontrado exitosamente' if usuario_encontrado else 'No se encontró el empleado seleccionado'
            elif criterio and valor:
                usuario_encontrado = modelo.buscar_empleado_por_criterio(connection, criterio, valor)
                mensaje = 'Empleado encontrado exitosamente' if usuario_encontrado else f'No se encontró ningún empleado con el criterio: {criterio} = "{valor}"'
            else:
                mensaje = 'Por favor selecciona un empleado del listado o especifica un criterio de búsqueda'
        except Exception as e:
            mensaje = 'Error al buscar empleado. Intenta nuevamente.'
            print(f"Error en búsqueda: {str(e)}")

        return render_template('Empleados/consultar_empleado.html', usuarios=usuarios, usuario_encontrado=usuario_encontrado, mensaje=mensaje)

@empleados_bp.route('/registrar_empleado', methods=['GET', 'POST'])
def registrar_empleado():
    if request.method == 'GET':
        return render_template('Empleados/registar_empleado.html')

    connection = current_app.connection
    datos_persona = (
        request.form['num_identificacion'],
        request.form['nombre'],
        request.form['apellido'],
        request.form['correo'],
        request.form.get('telefono', ''),
        request.form['tipo_documento']
    )
    password = request.form['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    datos_usuario = (
        hashed_password,
        'USER',
        'ACTIVO',
        datos_persona[0],
        datos_persona[5]
    )

    try:
        if modelo.persona_existente(connection, datos_persona[0]):
            flash('Ya existe una persona registrada con ese número de identificación', 'error')
            return render_template('Empleados/registar_empleado.html')

        if modelo.correo_existente(connection, datos_persona[3]):
            flash('Ya existe una cuenta con ese correo electrónico', 'error')
            return render_template('Empleados/registar_empleado.html')

        modelo.registrar_persona(connection, datos_persona)
        modelo.registrar_usuario(connection, datos_usuario)
        connection.commit()
        flash('Registro exitoso.', 'success')
    except Exception as e:
        connection.rollback()
        flash('Error al registrar usuario. Intenta nuevamente.', 'error')
        print(f"Error en registro: {str(e)}")

    return render_template('Empleados/registar_empleado.html')

@empleados_bp.route('/editar_empleado', methods=['GET', 'POST'])
def editar_empleado():
    connection = current_app.connection
    usuarios = []
    usuario_seleccionado = None
    mensaje = None

    try:
        usuarios = modelo.obtener_usuarios(connection)
    except Exception as e:
        flash('Error al cargar usuarios', 'error')
        print(f"Error al cargar usuarios: {str(e)}")

    if request.method == 'GET':
        id_usuario = request.args.get('id_usuario')
        if id_usuario:
            try:
                usuario_seleccionado = modelo.cargar_datos_edicion(connection, id_usuario)
                mensaje = 'Datos cargados exitosamente' if usuario_seleccionado else 'No se encontró el empleado especificado'
            except Exception as e:
                mensaje = 'Error al buscar empleado. Intenta nuevamente.'
                print(f"Error en búsqueda: {str(e)}")
        return render_template('Empleados/editar_empleado.html', usuarios=usuarios, usuario_seleccionado=usuario_seleccionado, mensaje=mensaje)

    if request.method == 'POST':
        accion = request.form.get('accion')

        if accion == 'cargar':
            id_usuario = request.form['id_usuario']
            try:
                usuario_seleccionado = modelo.cargar_datos_edicion(connection, id_usuario)
                mensaje = 'Datos cargados exitosamente' if usuario_seleccionado else 'No se encontró el empleado especificado'
            except Exception as e:
                mensaje = 'Error al cargar datos del empleado'
                print(f"Error al cargar datos: {str(e)}")

        elif accion == 'actualizar':
            id_usuario = request.form['id_usuario']
            nombre_completo = request.form['name']
            email = request.form['email']
            password = request.form.get('password', '')
            nombres = nombre_completo.split(' ')
            nombre = nombres[0]
            apellido = ' '.join(nombres[1:]) if len(nombres) > 1 else ''

            try:
                if not modelo.persona_existente(connection, id_usuario):
                    mensaje = 'El empleado no existe'
                elif modelo.correo_existente(connection, email, exclude_id=id_usuario):
                    mensaje = 'El correo electrónico ya está en uso por otro empleado'
                else:
                    modelo.actualizar_persona(connection, nombre, apellido, email, id_usuario)
                    if password:
                        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                        modelo.actualizar_contraseña(connection, hashed_password, id_usuario)
                    connection.commit()
                    mensaje = 'Usuario actualizado exitosamente'
                    usuario_seleccionado = modelo.cargar_datos_edicion(connection, id_usuario)
            except Exception as e:
                connection.rollback()
                mensaje = 'Error al actualizar empleado. Intenta nuevamente.'
                print(f"Error en actualización: {str(e)}")

        return render_template('Empleados/editar_empleado.html', usuarios=usuarios, usuario_seleccionado=usuario_seleccionado, mensaje=mensaje)

@empleados_bp.route('/eliminar_empleado', methods=['GET', 'POST'])
def eliminar_empleado():
    connection = current_app.connection
    usuarios = []
    mensaje = None

    try:
        usuarios = modelo.obtener_usuarios(connection)
    except Exception as e:
        mensaje = 'Error al cargar usuarios'
        print(f"Error al cargar usuarios: {str(e)}")

    if request.method == 'GET':
        return render_template('Empleados/eliminar_empleado.html', usuarios=usuarios, mensaje=mensaje)

    if request.method == 'POST':
        id_usuario = request.form['id_usuario']

        try:
            if not modelo.persona_existente(connection, id_usuario):
                mensaje = 'El empleado no existe'
            else:
                modelo.eliminar_usuario(connection, id_usuario)
                connection.commit()
                mensaje = 'Empleado eliminado exitosamente'
                usuarios = modelo.obtener_usuarios(connection)
        except Exception as e:
            connection.rollback()
            mensaje = 'Error al eliminar empleado. Intenta nuevamente.'
            print(f"Error en eliminación: {str(e)}")

        return render_template('Empleados/eliminar_empleado.html', usuarios=usuarios, mensaje=mensaje)
