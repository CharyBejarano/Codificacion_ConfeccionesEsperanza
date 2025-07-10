CREATE DATABASE mel_app;
USE mel_app;

-- Tabla: tipoDocumento
CREATE TABLE tipoDocumento (
    tipo_Doc VARCHAR(25) PRIMARY KEY,
    Estado TINYINT,
    descripcion VARCHAR(45)
);
-- Tabla: Persona
CREATE TABLE Persona (
    tipoDocumento_tipo_Doc VARCHAR(25),
    num_identificacion INT,
    Nombre VARCHAR(45),
    Apellido VARCHAR(45),
    Correo VARCHAR(45),
    Telefono INT,
    PRIMARY KEY (tipoDocumento_tipo_Doc, num_identificacion),
    FOREIGN KEY (tipoDocumento_tipo_Doc) REFERENCES tipoDocumento(tipo_Doc)
);
-- Tabla: Usuario
CREATE TABLE Usuario (
    Contraseña VARCHAR(255),
    Rol ENUM('administrador', 'asistente'),
    Estado VARCHAR(45),
    Persona_num_identificacion INT,
    Persona_tipoDocumento_tipo_Doc VARCHAR(25),
    PRIMARY KEY (Persona_tipoDocumento_tipo_Doc, Persona_num_identificacion),
    FOREIGN KEY (Persona_tipoDocumento_tipo_Doc, Persona_num_identificacion)
        REFERENCES Persona(tipoDocumento_tipo_Doc, num_identificacion)
);
-- Tabla: Cliente
CREATE TABLE Cliente (
    NIT INT PRIMARY KEY,
    Direccion VARCHAR(45),
    Persona_num_identificacion INT,
    Persona_tipoDocumento_tipo_Doc VARCHAR(25),
    FOREIGN KEY (Persona_tipoDocumento_tipo_Doc, Persona_num_identificacion)
        REFERENCES Persona(tipoDocumento_tipo_Doc, num_identificacion)
);
-- Tabla: Pedidos
CREATE TABLE Pedidos (
    id_pedido INT PRIMARY KEY AUTO_INCREMENT,
    fecha_registro DATE,
    fecha_entrega DATE,
    estado ENUM('pendiente', 'en_proceso', 'completado', 'entregado'),
    Cliente_Persona_num_identificacion INT,
    Cliente_Persona_tipoDocumento_tipo_Doc VARCHAR(25),
    FOREIGN KEY (Cliente_Persona_tipoDocumento_tipo_Doc, Cliente_Persona_num_identificacion)
        REFERENCES Persona(tipoDocumento_tipo_Doc, num_identificacion)
);
-- Tabla: Producto
CREATE TABLE Producto (
    idProducto INT PRIMARY KEY AUTO_INCREMENT,
    Tipo VARCHAR(45),
    descripcion VARCHAR(45),
    Pedidos_id_pedido INT,
    FOREIGN KEY (Pedidos_id_pedido) REFERENCES Pedidos(id_pedido)
);
-- Tabla: Tarea
CREATE TABLE Tarea (
    id_tarea INT PRIMARY KEY AUTO_INCREMENT,
    nombre_tarea VARCHAR(100),
    descripcion TEXT(100),
    Estado ENUM('pendiente', 'en_proceso', 'completada'),
    fecha_inicio DATE,
    fecha_fin DATE,
    comentarios TEXT(100)
);
-- Tabla intermedia: Tarea_Producto
CREATE TABLE Tarea_Producto (
    Producto_idProducto INT,
    Tarea_id_tarea INT,
    PRIMARY KEY (Producto_idProducto, Tarea_id_tarea),
    FOREIGN KEY (Producto_idProducto) REFERENCES Producto(idProducto),
    FOREIGN KEY (Tarea_id_tarea) REFERENCES Tarea(id_tarea)
);

-- Tabla intermedia: Tarea_Producto_has_Usuario
CREATE TABLE Tarea_Producto_has_Usuario (
    Tarea_Producto_Producto_idProducto INT,
    Tarea_Producto_Tarea_id_tarea INT,
    Usuario_Persona_num_identificacion INT,
    Usuario_Persona_tipoDocumento_tipo_Doc VARCHAR(25),
    PRIMARY KEY (Tarea_Producto_Producto_idProducto, Tarea_Producto_Tarea_id_tarea, Usuario_Persona_tipoDocumento_tipo_Doc, Usuario_Persona_num_identificacion),
    FOREIGN KEY (Tarea_Producto_Producto_idProducto, Tarea_Producto_Tarea_id_tarea)
        REFERENCES Tarea_Producto(Producto_idProducto, Tarea_id_tarea),
    FOREIGN KEY (Usuario_Persona_tipoDocumento_tipo_Doc, Usuario_Persona_num_identificacion)
        REFERENCES Usuario(Persona_tipoDocumento_tipo_Doc, Persona_num_identificacion)
);

-- Tabla: Material
CREATE TABLE Material (
    id_material INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100) NOT NULL,
    tipo_material VARCHAR(50),
    cantidad INT NOT NULL DEFAULT 0,
    Unidad_medida VARCHAR(20) NOT NULL,
    proveedor VARCHAR(100) NOT NULL,
    Fecha_entrada DATE NOT NULL
);

DROP Table IF EXISTS material;

-- Tabla intermedia: Producto_Material
CREATE TABLE Producto_Material (
    Material_id_material INT,
    Producto_idProducto INT,
    Cantidad DECIMAL(20,2),
    PRIMARY KEY (Material_id_material, Producto_idProducto),
    FOREIGN KEY (Material_id_material) REFERENCES Material(id_material),
    FOREIGN KEY (Producto_idProducto) REFERENCES Producto(idProducto)
);
INSERT INTO tipodocumento (tipo_Doc, Estado, descripcion)
VALUES 
('CC', 1, 'Cédula de Ciudadanía'),
('TI', 1, 'Tarjeta de Identidad'),
('NIT',1, 'Numero de Identificacion Tributaria'),
('CE', 1, 'Cédula de Extranjería');



CREATE DATABASE mel_app;
USE mel_app;