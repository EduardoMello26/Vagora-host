-- ============================================
-- Sistema de Gerenciamento de Estacionamento
-- Script SQL - MySQL Workbench
-- ============================================

CREATE DATABASE IF NOT EXISTS estacionamento CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE estacionamento;

-- ----------------------------------------
-- Tabela: usuario
-- ----------------------------------------
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'operador') NOT NULL DEFAULT 'operador',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------
-- Tabela: cliente
-- ----------------------------------------
CREATE TABLE cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    tipo ENUM('avulso', 'mensalista') NOT NULL DEFAULT 'avulso',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------
-- Tabela: veiculo
-- ----------------------------------------
CREATE TABLE veiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    placa VARCHAR(10) NOT NULL UNIQUE,
    modelo VARCHAR(80),
    cor VARCHAR(40),
    CONSTRAINT fk_veiculo_cliente FOREIGN KEY (cliente_id) REFERENCES cliente(id) ON DELETE SET NULL
);

-- ----------------------------------------
-- Tabela: vaga
-- ----------------------------------------
CREATE TABLE vaga (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(10) NOT NULL UNIQUE,
    tipo ENUM('carro', 'moto', 'deficiente', 'idoso') NOT NULL DEFAULT 'carro',
    status ENUM('livre', 'ocupada') NOT NULL DEFAULT 'livre'
);

-- ----------------------------------------
-- Tabela: tarifa
-- ----------------------------------------
CREATE TABLE tarifa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL,
    valor_hora DECIMAL(8,2) NOT NULL,
    valor_diaria DECIMAL(8,2),
    tipo_veiculo ENUM('carro', 'moto', 'todos') NOT NULL DEFAULT 'todos'
);

-- ----------------------------------------
-- Tabela: ticket
-- ----------------------------------------
CREATE TABLE ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    veiculo_id INT NOT NULL,
    vaga_id INT NOT NULL,
    usuario_id INT NOT NULL,
    entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    saida DATETIME,
    status ENUM('aberto', 'finalizado', 'cancelado') NOT NULL DEFAULT 'aberto',
    CONSTRAINT fk_ticket_veiculo FOREIGN KEY (veiculo_id) REFERENCES veiculo(id),
    CONSTRAINT fk_ticket_vaga FOREIGN KEY (vaga_id) REFERENCES vaga(id),
    CONSTRAINT fk_ticket_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- ----------------------------------------
-- Tabela: pagamento
-- ----------------------------------------
CREATE TABLE pagamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    tarifa_id INT NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('dinheiro', 'cartao_debito', 'cartao_credito', 'pix') NOT NULL,
    pago_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagamento_ticket FOREIGN KEY (ticket_id) REFERENCES ticket(id),
    CONSTRAINT fk_pagamento_tarifa FOREIGN KEY (tarifa_id) REFERENCES tarifa(id)
);

-- ----------------------------------------
-- Tabela: avaria
-- ----------------------------------------
CREATE TABLE avaria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    usuario_id INT NOT NULL,
    descricao TEXT NOT NULL,
    registrado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avaria_ticket FOREIGN KEY (ticket_id) REFERENCES ticket(id),
    CONSTRAINT fk_avaria_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);