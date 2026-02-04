-- MySQL schema for BiciCenter (generated from Django models in menu/models.py)
-- Replace `bicicenter_db` with the database name you want.

CREATE DATABASE IF NOT EXISTS `bicicenter_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `bicicenter_db`;

CREATE TABLE IF NOT EXISTS `menu_bicicleta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `modelo` varchar(255) DEFAULT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
  `imagen` varchar(200) DEFAULT NULL,
  `tipo` varchar(50) NOT NULL DEFAULT 'city',
  `color` varchar(20) DEFAULT NULL,
  `stock` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `menu_repuesto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
  `imagen` varchar(200) DEFAULT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `marca` varchar(100) DEFAULT NULL,
  CREATE DATABASE IF NOT EXISTS `bicicenter_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  USE `bicicenter_db`;

  CREATE TABLE IF NOT EXISTS `menu_bicicleta` (
    `id` int NOT NULL AUTO_INCREMENT,
    `nombre` varchar(255) NOT NULL,
    `marca` varchar(100) DEFAULT NULL,
    `modelo` varchar(255) DEFAULT NULL,
    `descripcion` text,
    `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
    `imagen` varchar(200) DEFAULT NULL,
    `tipo` varchar(50) NOT NULL DEFAULT 'city',
    `color` varchar(20) DEFAULT NULL,
    `stock` int NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_repuesto` (
    `id` int NOT NULL AUTO_INCREMENT,
    `nombre` varchar(255) NOT NULL,
    `descripcion` text,
    `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
    `imagen` varchar(200) DEFAULT NULL,
    `categoria` varchar(100) DEFAULT NULL,
    `marca` varchar(100) DEFAULT NULL,
    `numero_parte` varchar(100) DEFAULT NULL,
    `compatibilidad` text,
    `stock` int NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_accesorio` (
    `id` int NOT NULL AUTO_INCREMENT,
    `nombre` varchar(255) NOT NULL,
    `descripcion` text,
    `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
    `imagen` varchar(200) DEFAULT NULL,
    `categoria` varchar(100) DEFAULT NULL,
    `marca` varchar(100) DEFAULT NULL,
    `stock` int NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_cliente` (
    `id` int NOT NULL AUTO_INCREMENT,
    `nombre` varchar(100) NOT NULL,
    `apellido` varchar(100) NOT NULL,
    `rut` varchar(12) NOT NULL,
    `email` varchar(254) NOT NULL,
    `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `menu_cliente_rut_key` (`rut`),
    UNIQUE KEY `menu_cliente_email_key` (`email`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_serviciomantenimiento` (
    `id` int NOT NULL AUTO_INCREMENT,
    `nombre` varchar(50) NOT NULL,
    `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
    `descripcion` text,
    PRIMARY KEY (`id`),
    UNIQUE KEY `menu_serviciomantenimiento_nombre_key` (`nombre`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_bicicletacliente` (
    `id` int NOT NULL AUTO_INCREMENT,
    `cliente_id` int NOT NULL,
    `marca` varchar(50) NOT NULL,
    `color` varchar(20) NOT NULL,
    `tipo` varchar(20) NOT NULL,
    `anio` int DEFAULT NULL,
    `notas_adicionales` text,
    `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `menu_bicicletacliente_cliente_id_idx` (`cliente_id`),
    CONSTRAINT `menu_bicicletacliente_cliente_id_fk` FOREIGN KEY (`cliente_id`) REFERENCES `menu_cliente` (`id`) ON DELETE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_ordenmantenimiento` (
    `id` int NOT NULL AUTO_INCREMENT,
    `cliente_id` int NOT NULL,
    `bicicleta_id` int NOT NULL,
    `subtotal` decimal(10,2) NOT NULL DEFAULT 0.00,
    `iva` decimal(10,2) NOT NULL DEFAULT 0.00,
    `total` decimal(10,2) NOT NULL DEFAULT 0.00,
    `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
    `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `menu_ordenmantenimiento_cliente_id_idx` (`cliente_id`),
    KEY `menu_ordenmantenimiento_bicicleta_id_idx` (`bicicleta_id`),
    CONSTRAINT `menu_ordenmantenimiento_cliente_id_fk` FOREIGN KEY (`cliente_id`) REFERENCES `menu_cliente` (`id`) ON DELETE CASCADE,
    CONSTRAINT `menu_ordenmantenimiento_bicicleta_id_fk` FOREIGN KEY (`bicicleta_id`) REFERENCES `menu_bicicletacliente` (`id`) ON DELETE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE TABLE IF NOT EXISTS `menu_itemordenmantenimiento` (
    `id` int NOT NULL AUTO_INCREMENT,
    `orden_id` int NOT NULL,
    `servicio_id` int NOT NULL,
    `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (`id`),
    KEY `menu_itemordenmantenimiento_orden_id_idx` (`orden_id`),
    KEY `menu_itemordenmantenimiento_servicio_id_idx` (`servicio_id`),
    CONSTRAINT `menu_itemordenmantenimiento_orden_id_fk` FOREIGN KEY (`orden_id`) REFERENCES `menu_ordenmantenimiento` (`id`) ON DELETE CASCADE,
    CONSTRAINT `menu_itemordenmantenimiento_servicio_id_fk` FOREIGN KEY (`servicio_id`) REFERENCES `menu_serviciomantenimiento` (`id`) ON DELETE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

  CREATE INDEX `idx_cliente_email` ON `menu_cliente` (`email`);
  CREATE INDEX `idx_cliente_rut` ON `menu_cliente` (`rut`);
