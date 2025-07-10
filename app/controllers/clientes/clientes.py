from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from app.models import modelo_clientes as modelo

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
def mostrar_clientes():
    return render_template('clientes/clientes.html')


@clientes_bp.route('/consultar_cliente', methods=['GET', 'POST'])
def consultar_cliente():
    connection = current_app.connection
    clientes = [] 
    cliente_encontrado = None
    mensaje = None

    try:
        clientes = modelo.obtener_clientes(connection)
    except Exception as e:
        flash('Error al cargar la lista de clientes para consulta.', 'error')
        print(f"Error al cargar clientes en consultar_cliente: {str(e)}")

    if request.method == 'GET':
        num_identificacion_url = request.args.get('num_identificacion')
        tipo_documento_url = request.args.get('tipo_documento')

        if num_identificacion_url and tipo_documento_url:
            try:
                cliente_encontrado = modelo.buscar_cliente_por_identificacion(connection, num_identificacion_url, tipo_documento_url)
                if cliente_encontrado:
                    mensaje = 'Cliente encontrado exitosamente.'
                else:
                    mensaje = 'No se encontró el cliente especificado.'
            except Exception as e:
                mensaje = f'Error al buscar cliente desde URL: {str(e)}'
                print(f"Error al buscar cliente en consultar_cliente (GET por URL): {str(e)}")
        return render_template('Clientes/consultar_cliente.html', clientes=clientes, cliente_encontrado=cliente_encontrado, mensaje=mensaje)
    
    if request.method == 'POST':
        accion_select = request.form.get('accion_select')
        search_action = request.form.get('search_action')
        nit_cliente_seleccionado = request.form.get('nit_cliente') 

        criterio = request.form.get('criterio_busqueda')
        valor = request.form.get('valor_busqueda', '').strip()
        tipo_documento_busqueda = request.form.get('tipo_documento_busqueda')
        try:
            # Prioriza la búsqueda según el 'search_action' enviado por JS
            if search_action == 'search_by_list' and nit_cliente_seleccionado:
                # Si la acción es por lista y hay un NIT seleccionado
                cliente_encontrado = modelo.buscar_cliente_por_nit(connection, nit_cliente_seleccionado)
                if cliente_encontrado:
                    mensaje = 'Cliente encontrado exitosamente.'
                else:
                    mensaje = 'No se encontró el cliente seleccionado.'
            elif search_action == 'search_by_criterion' and criterio and valor:
                # Si la acción es por criterio y hay criterio/valor
                if criterio == 'num_identificacion':
                    if not tipo_documento_busqueda:
                        flash("Por favor, selecciona el tipo de documento para la búsqueda por número de identificación.", 'error')
                    else:
                        # Usar buscar_cliente_por_identificacion para num_identificacion y tipo_documento
                        cliente_encontrado = modelo.buscar_cliente_por_identificacion(connection, valor, tipo_documento_busqueda)
                elif criterio == 'NIT':
                    cliente_encontrado = modelo.buscar_cliente_por_nit(connection, valor)
                else: # Otros criterios como nombre, email
                    # Asegúrate de que buscar_cliente_por_criterio pueda manejar el parámetro tipo_documento_busqueda
                    # aunque no lo use para estos criterios, o ajusta la llamada si es necesario.
                    cliente_encontrado = modelo.buscar_cliente_por_criterio(connection, criterio, valor, tipo_documento_busqueda)
                
                if cliente_encontrado:
                    mensaje = f"Cliente {cliente_encontrado.get('Nombre', '')} {cliente_encontrado.get('Apellido', '')} encontrado exitosamente."
                else:
                    if not (criterio == 'num_identificacion' and not tipo_documento_busqueda):
                        mensaje = "No se encontró ningún cliente con ese criterio."
            else:
                # Este caso se ejecuta si no se seleccionó ninguna acción válida o faltan datos
                flash('Por favor, selecciona un cliente de la lista o ingresa un criterio y valor de búsqueda.', 'info')
        except Exception as e:
            mensaje = f'Error al buscar cliente: {str(e)}'
            print(f"Error en búsqueda: {str(e)}")
    
    # Renderiza la plantilla con los datos
    return render_template('Clientes/consultar_cliente.html', clientes=clientes, cliente_encontrado=cliente_encontrado, mensaje=mensaje)


@clientes_bp.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    """
    Ruta para registrar un nuevo cliente.
    """
    if request.method == 'GET':
        return render_template('Clientes/registrar_cliente.html')

    connection = current_app.connection
    
    # Datos de Persona
    num_identificacion = request.form['num_identificacion']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    correo = request.form['correo']
    telefono = request.form.get('telefono', '') 
    tipo_documento = request.form['tipo_documento']
    nit_cliente = request.form.get('razon_social', '') # Asumimos que 'razon_social' del form es el NIT del cliente
    direccion_cliente = request.form.get('direccion', '')

    try:
        # Validaciones de existencia
        if modelo.persona_existente(connection, num_identificacion, tipo_documento):
            flash('Ya existe una persona registrada con ese número y tipo de identificación.', 'error')
            return render_template('Clientes/registrar_cliente.html')

        if modelo.correo_existente(connection, correo):
            flash('Ya existe una cuenta con ese correo electrónico.', 'error')
            return render_template('Clientes/registrar_cliente.html')

        if modelo.cliente_existente(connection, nit_cliente): # Verifica si el NIT del cliente ya existe
            flash('Ya existe un cliente registrado con esa Razón Social (NIT).', 'error')
            return render_template('Clientes/registrar_cliente.html')

        # Registrar en la tabla Persona
        datos_persona = (
            num_identificacion,
            nombre,
            apellido,
            correo,
            telefono,
            tipo_documento
        )
        modelo.registrar_persona(connection, datos_persona)

        # Registrar en la tabla Cliente
        datos_cliente = (
            nit_cliente, # NIT del cliente
            direccion_cliente,
            num_identificacion, # FK Persona_num_identificacion
            tipo_documento      # FK Persona_tipoDocumento_tipo_Doc
        )
        modelo.registrar_cliente(connection, datos_cliente)

        connection.commit()
        flash('Cliente registrado exitosamente.', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error al registrar cliente: {str(e)}. Intenta nuevamente.', 'error')
        print(f"Error en registro de cliente: {str(e)}")

    return render_template('Clientes/registrar_cliente.html')


@clientes_bp.route('/editar_cliente', methods=['GET', 'POST'])
def editar_cliente():
    """
    Ruta para editar un cliente existente.
    """
    connection = current_app.connection # O get_db_connection() si es tu forma de obtener la conexión
    clientes_todos = [] # Lista de todos los clientes para el select de "Seleccionar Cliente"
    cliente_seleccionado = None
    mensaje = None

    try:
        clientes_todos = modelo.obtener_clientes(connection) # Cargar todos los clientes para el select
    except Exception as e:
        flash('Error al cargar clientes para edición.', 'error')
        print(f"Error al cargar clientes en editar_cliente (GET/POST inicial): {str(e)}")

    if request.method == 'GET':
        
        num_identificacion_url = request.args.get('num_identificacion')
        tipo_documento_url = request.args.get('tipo_documento')

        if num_identificacion_url and tipo_documento_url:
            try:
                cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, num_identificacion_url, tipo_documento_url)
                if cliente_seleccionado:
                    mensaje = 'Datos cargados exitosamente.'
                else:
                    mensaje = 'No se encontró el cliente especificado.'
            except Exception as e:
                mensaje = f'Error al cargar datos del cliente desde URL: {str(e)}'
                print(f"Error al cargar datos en editar_cliente (GET por URL): {str(e)}")
        
        # Siempre renderiza la plantilla con lo que se tenga
        return render_template('Clientes/editar_cliente.html', clientes_todos=clientes_todos, cliente_seleccionado=cliente_seleccionado, mensaje=mensaje)

    if request.method == 'POST':
        accion = request.form.get('accion') # Usamos .get() para evitar KeyError

        if accion == 'cargar':
            # Viene de seleccionar un cliente en el dropdown y presionar "Cargar"
            # Asumo que el dropdown envía un valor como "NUM_IDENTIFICACION|TIPO_DOC"
            cliente_id_completo = request.form.get('cliente_a_editar') # Asegúrate que el name del select sea 'cliente_a_editar'

            if cliente_id_completo:
                try:
                    num_identificacion, tipo_documento = cliente_id_completo.split('|')
                    cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, num_identificacion, tipo_documento)
                    if cliente_seleccionado:
                        flash('Datos cargados exitosamente.', 'success')
                    else:
                        flash('No se encontró el cliente especificado para cargar.', 'error')
                except ValueError:
                    flash('Formato de ID de cliente inválido.', 'error')
                except Exception as e:
                    flash(f'Error al cargar datos del cliente: {str(e)}', 'error')
                    print(f"Error al cargar datos en editar_cliente (accion=cargar): {str(e)}")
            else:
                flash('Por favor, selecciona un cliente para cargar.', 'warning')

        elif accion == 'actualizar':

            original_num_identificacion = request.form.get('original_num_identificacion', '')
            original_tipo_documento = request.form.get('original_tipo_documento', '')
            original_nit_cliente = request.form.get('original_nit_cliente', '')

            nuevo_num_identificacion = request.form.get('num_identificacion', '')
            nuevo_tipo_documento = request.form.get('tipo_documento', '')
            nuevo_nombre_completo = request.form.get('nombre_cliente', '')
            nuevo_correo = request.form.get('correo', '')
            nuevo_telefono = request.form.get('telefono', '')
            nuevo_nit = request.form.get('nit_cliente', '')
            nueva_direccion = request.form.get('cliente_direccion', '')
            
            nuevo_nombre = ''
            nuevo_apellido = ''
            if nuevo_nombre_completo:
                partes_nombre = nuevo_nombre_completo.split(' ')
                if len(partes_nombre) > 1:
                    nuevo_apellido = partes_nombre[-1]
                    nuevo_nombre = ' '.join(partes_nombre[:-1])
                else:
                    nuevo_nombre = nuevo_nombre_completo
                    nuevo_apellido = ''
            if not all([original_num_identificacion, original_tipo_documento,
                            nuevo_num_identificacion, nuevo_tipo_documento, # Los nuevos ID también son obligatorios si se editan
                            nuevo_nombre_completo, nuevo_correo, nuevo_telefono,
                            nuevo_nit, nueva_direccion]):
                flash('Todos los campos son obligatorios. Por favor, revisa.', 'error')
                # Si hay error de validación, intenta recargar el cliente seleccionado o pre-llenar los campos
                if original_num_identificacion and original_tipo_documento:
                    cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, original_num_identificacion, original_tipo_documento)
                if not cliente_seleccionado: # Si no se pudo cargar, usa los datos enviados para pre-llenar
                    cliente_seleccionado = {
                        'num_identificacion': nuevo_num_identificacion, # Usar los nuevos valores si el ID original no existe
                        'tipoDocumento_tipo_Doc': nuevo_tipo_documento,
                        'nombre_cliente': nuevo_nombre_completo,
                        'Correo': nuevo_correo,
                        'Telefono': nuevo_telefono,
                        'NIT': nuevo_nit,
                        'cliente_direccion': nueva_direccion
                    }
                return render_template('Clientes/editar_cliente.html', clientes_todos=clientes_todos, cliente_seleccionado=cliente_seleccionado, mensaje=None)
            try:
                # Validación de correo existente (usando los originales para excluir al mismo cliente)
                if modelo.correo_existente(connection, nuevo_correo,
                                            exclude_num_identificacion=original_num_identificacion,
                                              exclude_tipo_documento=original_tipo_documento):
                    flash('El correo electrónico ya está en uso por otro cliente.', 'error')
                    cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, original_num_identificacion, original_tipo_documento)
                    return render_template('Clientes/editar_cliente.html', clientes_todos=clientes_todos, cliente_seleccionado=cliente_seleccionado, mensaje=None)

                datos_persona_para_actualizar = (
                    nuevo_num_identificacion,     # Para SET num_identificacion = %s
                    nuevo_nombre,                 # Para SET Nombre = %s
                    nuevo_apellido,  
                    nuevo_correo,                 # Para SET Correo = %s
                    nuevo_telefono,               # Para SET Telefono = %s
                    nuevo_tipo_documento,         # Para SET tipoDocumento_tipo_Doc = %s
                    original_num_identificacion,  # Para WHERE num_identificacion = %s
                    original_tipo_documento       # Para WHERE tipoDocumento_tipo_Doc = %s
                )

                modelo.actualizar_persona_db(connection, datos_persona_para_actualizar)


                datos_cliente_para_actualizar = (
                    nuevo_nit,                     # Para SET NIT = %s
                    nueva_direccion,               # Para SET Direccion = %s
                    nuevo_num_identificacion,      # Para SET Persona_num_identificacion = %s (el nuevo ID de Persona si cambió)
                    nuevo_tipo_documento,          # Para SET Persona_tipoDocumento_tipo_Doc = %s (el nuevo Tipo Doc de Persona si cambió)
                    original_num_identificacion,   # Para WHERE Persona_num_identificacion = %s
                    original_tipo_documento,       # Para WHERE Persona_tipoDocumento_tipo_Doc = %s
                    original_nit_cliente
                )
           
                modelo.actualizar_cliente_db(connection, datos_cliente_para_actualizar)
                connection.commit()
                flash('Cliente actualizado exitosamente.', 'success')

                cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, nuevo_num_identificacion, nuevo_tipo_documento)

                return redirect(url_for('clientes.editar_cliente',
                                 num_identificacion=nuevo_num_identificacion,
                                 tipo_documento=nuevo_tipo_documento))
            
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar cliente: {str(e)}. Intenta nuevamente.', 'error')
                print(f"Error en actualización de cliente: {str(e)}")
        # En caso de error, intentar recargar el cliente original o pre-llenar con los datos enviados
                if original_num_identificacion and original_tipo_documento:
                    cliente_seleccionado = modelo.buscar_cliente_por_identificacion(connection, original_num_identificacion, original_tipo_documento)
                if not cliente_seleccionado: # Si no se pudo cargar, usa los datos enviados para pre-llenar
                    cliente_seleccionado = {
                        'num_identificacion': nuevo_num_identificacion,
                        'tipoDocumento_tipo_Doc': nuevo_tipo_documento,
                        'nombre_cliente': nuevo_nombre_completo,
                        'Correo': nuevo_correo,
                        'Telefono': nuevo_telefono,
                        'NIT': nuevo_nit,
                        'cliente_direccion': nueva_direccion
                    }

# Este `return render_template` es el final del bloque POST si no hubo redirección
        return render_template('Clientes/editar_cliente.html', clientes_todos=clientes_todos, cliente_seleccionado=cliente_seleccionado, mensaje=mensaje)
            


@clientes_bp.route('/eliminar_cliente', methods=['GET', 'POST'])
def eliminar_cliente():
    """
    Ruta para eliminar un cliente.
    """
    connection = current_app.connection
    clientes = []
    mensaje = None

    try:
        clientes = modelo.obtener_clientes(connection) # Cargar todos los clientes para el select
    except Exception as e:
        flash('Error al cargar clientes para eliminación.', 'error')
        print(f"Error al cargar clientes en eliminar_cliente: {str(e)}")

    if request.method == 'POST':
        # Los campos ocultos num_identificacion y tipo_documento son rellenados por JS
        num_identificacion = request.form['num_identificacion_hidden']
        tipo_documento = request.form['tipo_documento_hidden']

        try:
            # Primero verifica si la persona existe para dar un mensaje más específico
            if not modelo.persona_existente(connection, num_identificacion, tipo_documento):
                flash('El cliente (persona) no existe o ya ha sido eliminado.', 'error')
            else:
                # Eliminar el cliente y la persona asociada
                modelo.eliminar_cliente_db(connection, num_identificacion, tipo_documento)
                connection.commit()
                flash('Cliente y persona asociados eliminados exitosamente.', 'success')
                # Recargar la lista de clientes después de la eliminación
                clientes = modelo.obtener_clientes(connection)
        except Exception as e:
            connection.rollback()
            flash(f'Error al eliminar cliente: {str(e)}. Intenta nuevamente.', 'error')
            print(f"Error en eliminación de cliente: {str(e)}")

    # Siempre renderiza la plantilla, ya sea GET o después de un POST
    return render_template('Clientes/eliminar_cliente.html', clientes=clientes, mensaje=mensaje)