# Library Booking System (Flask Web Application)

![License](https://img.shields.io/badge/License-AGPL_v3-blue.svg)
![Issues](https://img.shields.io/github/issues/gandrea51/mini-library-manager)
![Last Commit](https://img.shields.io/github/last-commit/gandrea51/mini-library-manager)

## 🇬🇧 Description

This repository contains a simple web application developed with **Python** and **Flask** for managing:
- Books
- Courses
- Their bookings

The application includes:
- User login system
- Two user roles (member and admin)
- Basic dashboard
- Basic statistics (top visited/downloaded items)

The backend is based on Flask and MySQL, while the frontend uses HTML, CSS, JavaScript, Bootstrap, and Font Awesome.

This project was developed during a curricular internship and later used as the base for a Bachelor's thesis.

## 🇮🇹 Descrizione

Questo repository contiene una semplice applicazione web sviluppata con **Python** e **Flask** per gestire:
- Libri
- Corsi
- Le loro prenotazioni

L’applicazione include:
- Sistema di login
- Due ruoli utente (socio e admin)
- Dashboard di amministrazione
- Statistiche di base (elementi più visualizzati/scaricati)

Il backend utilizza Flask e MySQL, mentre il frontend è basato su HTML, CSS, JavaScript, Bootstrap e Font Awesome.

Il progetto è stato sviluppato durante un tirocinio curriculare ed è stato successivamente la base della tesi di laurea triennale.

---

## 🚀 Features / Funzionalità

- ✅ Login / Authentication
- ✅ User roles (member/admin)
- ✅ Book management (CRUD)
- ✅ Course management (CRUD)
- ✅ Booking system
- ✅ Basic statistics
- ✅ Simple dashboard

## 🧰 Technologies Used / Tecnologie utilizzate

- Python (3.8+ recommended)
- Flask
- MySQL
- HTML / CSS / JavaScript
- Bootstrap
- Font Awesome

## 📂 Project Structure / Struttura del progetto
```
Application/  
├── static/  
│   ├── styles.css  
│   └── img_logo.png  
├── templates/  
│   ├── index.html  
│   ├── ...  
│   └── welcome.html  
├── app.py  
├── requirements.txt  
└── Procfile
```

> ⚠️ The structure is intentionally simple.
> The original version was developed in Laravel, but due to platform constraints and limited time (only one month to refactor) the application was rewritten in Flask, requiring some structural compromises.

## 🧑‍🎓 Academic Work / Lavoro accademico

This project was developed during the curricular internship of the Bachelor’s Degree in Computer Science and has been used as the basis for the final thesis.

Questo progetto è stato sviluppato durante il tirocinio curricolare della Laurea Triennale in Informatica ed è stato utilizzato come base per la tesi di laurea.

## 🏗️ Installation / Installazione

### 1. Clone the repository

```bash
git clone https://github.com/gandrea51/mini-library-manager.git
cd mini-library-manager
```

### 2. Create a virtual environment and activate it / Creare un ambiente virtuale e attivarlo
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies / Installare dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configure a local MySQL database / Configurare il database
Create a database manually (for now).

### ▶️ Run the application / Avvio dell’applicazione
```bash
python app.py
```
Then open:
```bash
http://127.0.0.1:5000
```

## 🔐 User Registration / Registrazione utenti

Users must register manually through the UI.

Gli utenti devono registrarsi tramite interfaccia.

## 🔧 Future Improvements / Miglioramenti futuri

- Automatic SQL database generation script
- Refactor into Flask Blueprints
- Add logging system

## 🤝 Contributions / Contributi

Pull Requests are welcome!

Le Pull Request sono benvenute!

## 📜 License / Licenza

Released under the AGPL v3 license.

Rilasciato sotto licenza AGPL v3.

See the __LICENSE__ file for details.
