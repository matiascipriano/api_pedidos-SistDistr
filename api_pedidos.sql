/* ACA VA EL CODIGO SQL PARA INICIALIZAR LA BASE CUANDO LEVANTE*/

-- Table structure for table `centro`
DROP TABLE IF EXISTS centro;
CREATE TABLE centro (
  idCentro SERIAL PRIMARY KEY,
  nombre VARCHAR(45) NOT NULL,
  direccion VARCHAR(45) NOT NULL
);

-- Table structure for table `item`
DROP TABLE IF EXISTS item;
CREATE TABLE item (
  idItem SERIAL PRIMARY KEY,
  idMaterial INT NOT NULL,
  cantidad INT NOT NULL,
  CONSTRAINT fk_material FOREIGN KEY (idMaterial) REFERENCES material (idMaterial)
);

-- Table structure for table `material`
DROP TABLE IF EXISTS material;
CREATE TABLE material (
  idMaterial SERIAL PRIMARY KEY,
  nombre VARCHAR(45) NOT NULL,
  descripcion VARCHAR(45) NOT NULL
);

-- Table structure for table `pedido`
DROP TABLE IF EXISTS pedido;
CREATE TABLE pedido (
  idPedido SERIAL PRIMARY KEY,
  estado VARCHAR(20) NOT NULL,
  cliente VARCHAR(100) NOT NULL,
  idCentro INT,
  CONSTRAINT fk_centro FOREIGN KEY (idCentro) REFERENCES centro (idCentro)
);

-- Table structure for table `usuario`
DROP TABLE IF EXISTS usuario;
CREATE TABLE usuario (
  idUsuario SERIAL PRIMARY KEY,
  usuario VARCHAR(20) NOT NULL,
  contraseña VARCHAR(255) NOT NULL,
  nombre_completo VARCHAR(100) NOT NULL
);