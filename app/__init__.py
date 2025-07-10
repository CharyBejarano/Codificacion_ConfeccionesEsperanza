from flask import Flask
import pymysql.cursors 
from config import Config

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    from app.controllers.main import main_bp
    from app.controllers.empleados.empleados import empleados_bp
    from app.controllers.usuarios.usuarios import usuarios_bp
    from app.controllers.clientes.clientes import clientes_bp
    from app.controllers.material.material import material_bp
    from app.controllers.pedidos.pedidos import pedidos_bp
    from app.controllers.home.home import home_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(home_bp)

    app.config.from_object(Config)
   
    connection = pymysql.connect(
        host = app.config['MYSQL_HOST'],
        user = app.config['MYSQL_USER'],
        password = app.config['MYSQL_PASSWORD'],
        database = app.config['MYSQL_DB'],
        cursorclass = pymysql.cursors.DictCursor
    )
    app.connection = connection
    return app