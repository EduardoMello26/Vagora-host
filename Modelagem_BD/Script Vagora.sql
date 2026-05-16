CREATE DATABASE IF NOT EXISTS estacionamento CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE estacionamento;

CREATE TABLE auth_user (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    username     VARCHAR(150) NOT NULL UNIQUE,
    email        VARCHAR(254) NOT NULL,
    password     VARCHAR(128) NOT NULL,
    first_name   VARCHAR(150) NOT NULL DEFAULT '',
    last_name    VARCHAR(150) NOT NULL DEFAULT '',
    is_staff     TINYINT(1)   NOT NULL DEFAULT 0,
    is_active    TINYINT(1)   NOT NULL DEFAULT 1,
    is_superuser TINYINT(1)   NOT NULL DEFAULT 0,
    date_joined  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login   DATETIME     NULL
);

CREATE TABLE cliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14)  NOT NULL UNIQUE,
    telefone VARCHAR(20)  NULL,
    tipo ENUM('avulso', 'mensalista') NOT NULL DEFAULT 'avulso',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE veiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NULL,
    placa VARCHAR(10)  NOT NULL UNIQUE,
    modelo VARCHAR(80)  NULL,
    cor VARCHAR(40)  NULL,
    CONSTRAINT fk_veiculo_cliente
        FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        ON DELETE SET NULL
);


CREATE TABLE vaga (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT UNSIGNED NOT NULL UNIQUE,
    tipo ENUM('carro', 'moto', 'deficiente', 'idoso') NOT NULL DEFAULT 'carro',
    status ENUM('livre', 'ocupada') NOT NULL DEFAULT 'livre'
);


CREATE TABLE tarifa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100)   NOT NULL,
    valor_hora DECIMAL(8, 2)  NOT NULL,
    tipo_veiculo ENUM('carro', 'moto', 'todos') NOT NULL DEFAULT 'todos',
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    CONSTRAINT chk_tarifa_horario CHECK (hora_fim > hora_inicio)
);


CREATE TABLE ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    veiculo_id  INT NULL,
    vaga_id     INT NOT NULL,
    operador_id INT NOT NULL,
    cliente_id  INT NULL,
    entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    saida DATETIME NULL,
    status ENUM('aberto', 'finalizado', 'cancelado') NOT NULL DEFAULT 'aberto',
    CONSTRAINT fk_ticket_veiculo
        FOREIGN KEY (veiculo_id)  REFERENCES veiculo(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticket_vaga
        FOREIGN KEY (vaga_id)     REFERENCES vaga(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticket_operador
        FOREIGN KEY (operador_id) REFERENCES auth_user(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ticket_cliente
        FOREIGN KEY (cliente_id)  REFERENCES cliente(id)
        ON DELETE RESTRICT
);


CREATE TABLE pagamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    tarifa_id INT NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('dinheiro', 'cartao_debito', 'cartao_credito', 'pix') NOT NULL,
    pago_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pagamento_ticket
        FOREIGN KEY (ticket_id)  REFERENCES ticket(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pagamento_tarifa
        FOREIGN KEY (tarifa_id)  REFERENCES tarifa(id)
        ON DELETE CASCADE
);


CREATE TABLE avaria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    veiculo_id INT NOT NULL,
    operador_id INT NOT NULL,
    descricao TEXT NOT NULL,
    registrado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avaria_veiculo
        FOREIGN KEY (veiculo_id)  REFERENCES veiculo(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_avaria_operador
        FOREIGN KEY (operador_id) REFERENCES auth_user(id)
        ON DELETE CASCADE
);