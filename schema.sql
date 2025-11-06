CREATE SCHEMA my_application;
USE my_application;

CREATE TABLE Utente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    ruolo ENUM('Admin', 'Socio') NOT NULL
);

CREATE TABLE Libro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titolo VARCHAR(255) NOT NULL,
    anno VARCHAR(255) NOT NULL,
    classificazione VARCHAR(255) NOT NULL,
    posizione VARCHAR(255) NOT NULL,
    autore VARCHAR(255) NOT NULL,
    genere VARCHAR(255) NOT NULL,
    collana VARCHAR(255),
    editore VARCHAR(255) NOT NULL,
    note TEXT,
    copie INT NOT NULL,
    disponibile ENUM('Si', 'No') NOT NULL DEFAULT 'Si',
    libro_mese VARCHAR(255) NOT NULL DEFAULT 'No',
    rivista VARCHAR(255) NOT NULL DEFAULT 'No',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    viste INT NOT NULL DEFAULT 0,
    download INT NOT NULL DEFAULT 0
);

CREATE TABLE Prestito (
    id  INT AUTO_INCREMENT PRIMARY KEY,
    uscita DATE NOT NULL,
    rientro DATE NOT NULL,
    terminato VARCHAR(2) NOT NULL DEFAULT 'No',
    prorogato VARCHAR(2) NOT NULL DEFAULT 'No',
    libro_id INT NOT NULL,
    utente_id INT NOT NULL,
    FOREIGN KEY (libro_id) REFERENCES Libro(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (utente_id) REFERENCES Utente(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Corso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    programma TEXT NOT NULL,
    docente VARCHAR(255) NOT NULL,
    giorno VARCHAR(255) NOT NULL,
    lezioni INT NOT NULL,
    note TEXT,
    partenza DATE,
    minimo INT NOT NULL,
    massimo INT NOT NULL,
    contributo DECIMAL(5, 2) NOT NULL,
    tessera DECIMAL(5, 2) NOT NULL,
    prenotazioni INT NOT NULL DEFAULT 0,
    iscrizioni INT NOT NULL DEFAULT 0,
    viste INT NOT NULL DEFAULT 0
);

CREATE TABLE Prenotazione (
    id  INT AUTO_INCREMENT PRIMARY KEY,
    stato VARCHAR(255) NOT NULL DEFAULT 'In attesa',
    corso_id INT NOT NULL,
    utente_id INT NOT NULL,
    FOREIGN KEY (corso_id) REFERENCES Corso(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (utente_id) REFERENCES Utente(id) ON UPDATE CASCADE ON DELETE CASCADE
);