from flask import Blueprint, render_template

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@pedidos_bp.route('/')
def mostrar_pedidos():
    return render_template('pedidos/pedidos.html')

@pedidos_bp.route('/control_pedidos',methods=['GET', 'POST'])
def control_pedidos():
    return render_template('pedidos/control_pedidos.html')