-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 21-11-2025 a las 18:19:04
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bd_restaurante`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias_menu`
--

CREATE TABLE `categorias_menu` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_cambios`
--

CREATE TABLE `historial_cambios` (
  `id_historial` int(11) NOT NULL,
  `id_registro` int(11) NOT NULL,
  `id_usuario_modifico` int(11) DEFAULT NULL,
  `fecha_cambio` datetime DEFAULT current_timestamp(),
  `descripcion_cambio` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mesas`
--

CREATE TABLE `mesas` (
  `id_mesa` int(11) NOT NULL,
  `numero_mesa` varchar(10) NOT NULL,
  `estado` varchar(50) DEFAULT 'disponible'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `restaurante`
--

CREATE TABLE `restaurante` (
  `id_registro` int(11) NOT NULL,
  `nombre_cliente` varchar(200) NOT NULL,
  `mesa` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT current_timestamp(),
  `items` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`items`)),
  `total` decimal(10,2) NOT NULL,
  `estado` varchar(50) DEFAULT 'Pendiente',
  `id_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `restaurante`
--

INSERT INTO `restaurante` (`id_registro`, `nombre_cliente`, `mesa`, `fecha_hora`, `items`, `total`, `estado`, `id_usuario`) VALUES
(6, 'emily', '5', '2025-11-10 21:02:57', '[{\"nombre\": \"Gordita - ASADO C/ROJO\", \"cantidad\": 1, \"precio_unitario\": 21.0, \"subtotal\": 21.0}, {\"nombre\": \"Gordita - DESHEBRADA S/CHILE\", \"cantidad\": 2, \"precio_unitario\": 21.0, \"subtotal\": 42.0}, {\"nombre\": \"Burro - ASADO C/VERDE\", \"cantidad\": 2, \"precio_unitario\": 36.0, \"subtotal\": 72.0}, {\"nombre\": \"Chile c/carne\", \"cantidad\": 1, \"precio_unitario\": 48.0, \"subtotal\": 48.0}]', 183.00, 'Pendiente', 1),
(7, 'jose', '16', '2025-11-11 11:35:52', '[{\"nombre\": \"Burro - ASADO C/ROJO\", \"cantidad\": 3, \"precio_unitario\": 36.0, \"subtotal\": 108.0}]', 108.00, 'Pendiente', 1),
(8, 'bravo', '8', '2025-11-13 10:10:34', '[{\"nombre\": \"Gordita - ASADO C/ROJO\", \"cantidad\": 1, \"precio_unitario\": 21.0, \"subtotal\": 21.0}, {\"nombre\": \"Gordita - BISTECK\", \"cantidad\": 2, \"precio_unitario\": 21.0, \"subtotal\": 42.0}]', 63.00, 'Pendiente', 1),
(9, 'mica', '2', '2025-11-14 09:31:23', '[{\"nombre\": \"Gordita - ASADO C/ROJO\", \"cantidad\": 1, \"precio_unitario\": 21.0, \"subtotal\": 21.0}]', 21.00, 'Pendiente', 1),
(11, 'meca', '1', '2025-11-14 10:18:20', '[{\"nombre\": \"Gordita - ASADO C/ROJO\", \"cantidad\": 1, \"precio_unitario\": 21.0, \"subtotal\": 21.0}]', 21.00, 'Pendiente', 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `usuario` varchar(100) NOT NULL,
  `gmail` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `rol` varchar(50) DEFAULT 'mesero'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `usuario`, `gmail`, `password_hash`, `rol`) VALUES
(1, 'admin', 'admin@correo.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'),
(2, 'Ana Torres', 'ana@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(3, 'Luis Cruz', 'luis@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(4, 'Maria Solis', 'maria@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(5, 'Carlos Diaz', 'carlos@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(6, 'Sofia Vera', 'sofia@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(7, 'Javier Ruiz', 'javier@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(8, 'Laura Mendi', 'laura@correo.com', '51838d20209b0878a87141aa9f5c001db79c9c130a4c2f6192f1bcc5ced778cc', 'mesero'),
(9, 'Jefe de Cocina', 'cocina@correo.com', '17fb2b2ef0554390dfdcb2eb9099e1279e12bd4b4b01fb33a1d5f4c0ce15e85c', 'cocina');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `id_venta` int(11) NOT NULL,
  `id_registro` int(11) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `total` decimal(10,2) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`id_venta`, `id_registro`, `fecha`, `total`, `id_usuario`) VALUES
(2, 6, '2025-11-10 21:02:57', 183.00, 1),
(3, 7, '2025-11-11 11:35:52', 108.00, 1),
(4, 8, '2025-11-13 10:10:34', 63.00, 1),
(5, 9, '2025-11-14 09:31:23', 21.00, 1),
(7, 11, '2025-11-14 10:18:20', 21.00, 6);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categorias_menu`
--
ALTER TABLE `categorias_menu`
  ADD PRIMARY KEY (`id_categoria`),
  ADD UNIQUE KEY `nombre_categoria` (`nombre_categoria`);

--
-- Indices de la tabla `historial_cambios`
--
ALTER TABLE `historial_cambios`
  ADD PRIMARY KEY (`id_historial`),
  ADD KEY `id_registro` (`id_registro`),
  ADD KEY `id_usuario_modifico` (`id_usuario_modifico`);

--
-- Indices de la tabla `mesas`
--
ALTER TABLE `mesas`
  ADD PRIMARY KEY (`id_mesa`),
  ADD UNIQUE KEY `numero_mesa` (`numero_mesa`);

--
-- Indices de la tabla `restaurante`
--
ALTER TABLE `restaurante`
  ADD PRIMARY KEY (`id_registro`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `usuario` (`usuario`),
  ADD UNIQUE KEY `gmail` (`gmail`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`id_venta`),
  ADD KEY `id_registro` (`id_registro`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias_menu`
--
ALTER TABLE `categorias_menu`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `historial_cambios`
--
ALTER TABLE `historial_cambios`
  MODIFY `id_historial` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mesas`
--
ALTER TABLE `mesas`
  MODIFY `id_mesa` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `restaurante`
--
ALTER TABLE `restaurante`
  MODIFY `id_registro` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `id_venta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `historial_cambios`
--
ALTER TABLE `historial_cambios`
  ADD CONSTRAINT `historial_cambios_ibfk_1` FOREIGN KEY (`id_registro`) REFERENCES `restaurante` (`id_registro`) ON DELETE CASCADE,
  ADD CONSTRAINT `historial_cambios_ibfk_2` FOREIGN KEY (`id_usuario_modifico`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `restaurante`
--
ALTER TABLE `restaurante`
  ADD CONSTRAINT `restaurante_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`id_registro`) REFERENCES `restaurante` (`id_registro`) ON DELETE CASCADE,
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
