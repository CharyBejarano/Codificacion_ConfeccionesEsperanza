from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug = True)

try:
    from models.modelo_usuarios import UsuarioModel
    print("✅ Modelo importado correctamente")
except ImportError as e:
    print(f"❌ Error al importar modelo: {e}")