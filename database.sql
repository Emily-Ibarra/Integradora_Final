
DROP DATABASE IF EXISTS restaurante_mvc_db;
CREATE DATABASE IF NOT EXISTS restaurante_mvc_db;
USE restaurante_mvc_db;

CREATE TABLE usuarios (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'usuario'
);

INSERT INTO usuarios (usuario, password, rol) VALUES ('admin', '1234', 'administrador');

CREATE TABLE menu_items (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0
);

INSERT INTO menu_items (nombre, categoria, precio, stock) VALUES
('Gordita - ASADO C/ROJO', 'Gorditas', 21.00, 100),
('Burro - ASADO C/ROJO', 'Burros', 36.00, 100),
('Carnitas (kg)', 'Por Kilo', 320.00, 50),
('Chile c/queso', 'Extras', 35.00, 80);