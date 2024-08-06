from flask import *
from flask_sqlalchemy import *
from flask_login import *
from werkzeug.security import *
from sqlalchemy import *
from datetime import *
from xhtml2pdf import pisa
import math
import tempfile
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'why would I tell you my secret key?'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://andrea:password@localhost/Ancescao'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

# Classe Utente
class Utente(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    ruolo = db.Column(db.String(100))

# Classe Testo
class Testo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posizione = db.Column(db.String(255), unique=True, nullable=False) 
    testo = db.Column(db.Text, nullable=False)   

# Metodo per otterenere le informazioni sull'utente loggato nelle varie pagine
@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return {'current_user': current_user}
    return {'current_user': None}

@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return db.session.get(Utente, user_id)

# Metodo per la conversione in PDF
def convert_html_to_pdf(source_html):
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pisa_status = pisa.CreatePDF(source_html, dest=pdf_file)
    if pisa_status.err:
        print("Errore durante la creazione del PDF:", pisa_status.err)
    pdf_file.close()
    return pdf_file.name

# Controlli alla password
def is_password_valid(password):
    if len(password) < 8:
        return False, "La password deve contenere almeno 8 caratteri."
    if not re.search("[a-z]", password):
        return False, "La password deve contenere almeno una lettera minuscola."
    if not re.search("[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola."
    if not re.search("[0-9]", password):
        return False, "La password deve contenere almeno un numero."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): 
        return False, "La password deve contenere almeno un simbolo."
    return True, ""

def is_email_valid(email):
    if Utente.query.filter_by(email = email).first() is not None:
        return False, "L'indirizzo email è già presente."
    return True, ""

# Welcome --> Pagina esterna
@app.route('/')
def welcome():
    testo = Testo.query.filter_by(posizione = 'welcome').first()
    return render_template('welcome.html', testo = testo)

# Home --> Pagina interna
# Login_required --> che quella rotta richiede che un utente sia loggato
@app.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.ruolo == 'Amministratore':
            user_count = Utente.query.filter_by(ruolo='Socio').count()
            prestiti_in_corso = Prestito.query.filter_by(terminato="No").count()
            prenotazioni_count = Prenotazioni.query.count()
            return render_template('home.html', utente = current_user, user_count = user_count,
                prestiti_in_corso = prestiti_in_corso,
                prenotazioni_count = prenotazioni_count)
        else:
            return render_template('home.html', utente = current_user)
    else:
        return redirect(url_for(login))

# Documentazione online
@app.route('/documentazione')
@login_required
def info():
    return render_template('documentazione.html')

# Registrazione
@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        is_valid, error_message = is_email_valid(email)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('registrazione'))
        
        password = request.form.get('password')
        is_valid, error_message = is_password_valid(password)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('registrazione'))
        password = generate_password_hash(password)
        
        telefono = request.form.get('telefono')
        ruolo = request.form.get('ruolo')

        nuovo = Utente(nome = nome, email = email, password = password, telefono = telefono, ruolo = ruolo)
        db.session.add(nuovo)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('registrazione.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        utente = Utente.query.filter_by(email = email).first()
        if utente and check_password_hash(utente.password, password):
            login_user(utente)
            return redirect(url_for('home'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))

# Ripristino Password
@app.route('/cambia_password', methods=['GET', 'POST'])
def cambia_password():
    if request.method == 'POST':
        vecchia = request.form.get('vecchia')
        nuova = request.form.get('nuova')
        is_valid, error_message = is_password_valid(nuova)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('cambia_password'))
        nuova = generate_password_hash(nuova)

        # Verifica che la vecchia password sia corretta
        if check_password_hash(current_user.password, vecchia):
            current_user.password = generate_password_hash(nuova)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            # La vecchia password non è corretta
            return "La vecchia password non è corretta", 400

    return render_template('cambia_password.html')

# Ripristino Email
@app.route('/cambia_email', methods=['GET', 'POST'])
def cambia_email():
    if request.method == 'POST':
        nuova = request.form.get('nuova')

        # Verifica che la nuova email non sia già in uso
        if Utente.query.filter_by(email = nuova).first() is not None:
            return "L'email è già in uso", 400

        # Aggiorna l'email nel database
        current_user.email = nuova
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('cambia_email.html')

# Rotta Cambia Telefono
@app.route('/cambia_telefono', methods=['GET', 'POST'])
def cambia_telefono():
    if request.method == 'POST':
        nuovo = request.form.get('nuovo')

        # Aggiorna il numero nel database
        current_user.telefono = nuovo
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('cambia_telefono.html')

@app.route('/utente/<int:utente_id>')
@login_required
def gestisci_profilo(utente_id):      
    utente = db.session.get(Utente, utente_id)  
    # Inizializzare le variabili per i messaggi e i dati da passare alla view
    messaggio_prestiti = ""
    messaggio_prenotazioni = ""
    prestiti_attivi = []
    prenotazioni_attive = []

    # Ottenere i prestiti attivi
    prestiti = Prestito.query.filter_by(utente_id=utente.id, terminato="No").all()
    if prestiti:
        prestiti_attivi = prestiti
    else:
        messaggio_prestiti = "Non hai ancora effettuato prestiti.<br><br>Scopri la nostra selezione di titoli e approfitta delle offerte esclusive per il tuo prossimo prestito!"

    # Ottenere le prenotazioni attive
    prenotazioni = Prenotazioni.query.filter_by(utente_id=utente.id).all()
    if prenotazioni:
        prenotazioni_attive = prenotazioni
    else:
        messaggio_prenotazioni = "Non hai ancora effettuato prenotazioni.<br><br>Esplora i corsi disponibili e prenota subito le tue lezioni per approfittare delle offerte speciali!"

    # Passare i dati alla view
    return render_template('utente_profilo.html', 
                           utente=current_user,
                           prestiti_attivi=prestiti_attivi,
                           prenotazioni_attive=prenotazioni_attive,
                           messaggio_prestiti=messaggio_prestiti,
                           messaggio_prenotazioni=messaggio_prenotazioni)

# Modifica del Testo
@app.route('/testo/<int:testo_id>/edit', methods=['POST'])
@login_required
def edit_page(testo_id):
    testo = db.session.get(Testo, testo_id)    
    if request.method == 'POST':
        # Recupero la versione nuova 
        testo.testo = request.form['nuovo']
        # E aggiorno
        db.session.commit()

        return redirect(url_for('home'))

# Classe Libro
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(255), nullable=False)
    anno = db.Column(db.String(255), nullable=False)
    classificazione = db.Column(db.String(255), nullable=False)
    posizione = db.Column(db.String(255), nullable=False)
    autore = db.Column(db.String(255), nullable=False)
    genere = db.Column(db.String(255), nullable=False)
    collana = db.Column(db.String(255))
    editore = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)
    copie = db.Column(db.Integer, nullable=False)
    disponibile = db.Column(db.String(255), nullable=False)
    libro_mese = db.Column(db.String(255), nullable=False, default='No')
    rivista = db.Column(db.String(255), nullable=False, default='No')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    viste = db.Column(db.Integer, default=0)
    download = db.Column(db.Integer, default=0)

# Classe Prestito
class Prestito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uscita = db.Column(db.Date, nullable=False)
    rientro = db.Column(db.Date, nullable=False)
    terminato = db.Column(db.String(2), nullable=False)
    prorogato = db.Column(db.String(2), nullable=False)
    libro_id = db.Column(db.BigInteger, db.ForeignKey('libro.id'), nullable=False)
    utente_id = db.Column(db.BigInteger, db.ForeignKey('utente.id'), nullable=False)

    libro = db.relationship('Libro', backref=db.backref('prestiti', lazy=True))
    utente = db.relationship('Utente', backref=db.backref('prestiti', lazy=True))

# Index del Libro
@app.route('/libri')
def libro_index():
    if current_user.is_authenticated:
        # Libro del mese, se c'è
        month = Libro.query.filter_by(libro_mese = 'Si').first()
        # Trovo tutti i generi
        generi = Libro.query.with_entities(Libro.genere, func.count(Libro.genere)).group_by(Libro.genere).order_by(Libro.genere).all()
        # Recupero il testo corretto
        testo = Testo.query.filter_by(posizione = 'libro_index').first()
        # Statistiche
        total_books = Libro.query.count()
        total_view = db.session.query(db.func.sum(Libro.viste)).scalar() or 0
        total_downloads = db.session.query(db.func.sum(Libro.download)).scalar() or 0
        most_viewed_books = Libro.query.order_by(Libro.viste.desc()).limit(5).all()
        stats = {
            'total_books': total_books,
            'total_views': total_view,
            'total_downloads': total_downloads,
            'most_viewed_books': most_viewed_books
        }

        return render_template('libro_index.html', month = month, generi = generi, testo = testo, stats = stats)
    else:
        # Mostra contenuto per utenti non loggati
        generi = Libro.query.with_entities(Libro.genere, func.count(Libro.genere)).group_by(Libro.genere).order_by(Libro.genere).all()     
        testo = Testo.query.filter_by(posizione = 'libro_index').first()
        
        return render_template('libro_non_loggato.html', generi = generi, testo = testo)

# Libri di un certo genere
@app.route('/libri/<genere>')
@login_required
def libro_genere(genere):
    # Query
    libri = Libro.query.filter_by(genere = genere).order_by(Libro.titolo).all()
    testo = Testo.query.filter_by(posizione = 'libro_index').first()
    
    return render_template('libro_genere.html', libri = libri, testo = testo)

# Stampa dei libri del genere scelto
@app.route('/libri/<genere>/pdf')
@login_required
def libro_pdf(genere):
    # Query
    libri = Libro.query.filter_by(genere = genere).order_by(Libro.titolo).all()
    # Conversione
    html_string = render_template('libro_generePDF.html', libri = libri)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Ricerca per Titolo
@app.route('/libri/titolo', methods=['POST'])
@login_required
def libro_titolo():
    titolo = request.form.get('titolo')
    # Query
    libri = Libro.query.filter(Libro.titolo.like(f'%{titolo}%')).all()
    testo = Testo.query.filter_by(posizione = 'libro_index').first()
    
    return render_template('libro_titolo.html', libri = libri, testo = testo)

# Ricerca per Autore
@app.route('/libri/autore', methods=['POST'])
@login_required
def libro_autore():
    autore = request.form.get('nome')
    # Query
    libri = Libro.query.filter(Libro.autore.like(f'%{autore}%')).all()
    testo = Testo.query.filter_by(posizione = 'libro_index').first()
    
    return render_template('libro_autore.html', libri = libri, testo = testo)

# Ricerca per Genere
@app.route('/libri/genere', methods=['POST'])
@login_required
def libro_rgenere():
    genere = request.form.get('nome')
    # Query
    libri = Libro.query.filter(Libro.genere.like(f'%{genere}%')).all()
    testo = Testo.query.filter_by(posizione = 'libro_index').first()
    
    return render_template('libro_rgenere.html', libri = libri, testo = testo)

# Show di un libro
@app.route('/libro/<int:libro_id>')
@login_required
def libro_show(libro_id):
    # Query
    libro = db.session.get(Libro, libro_id)
    prestiti = Prestito.query.filter_by(libro_id = libro.id).all()
    testo = Testo.query.filter_by(posizione = 'libro_index').first()
    # Imposto i testi da mostrare
    libro.viste += 1
    db.session.commit()
    copie = ''
    rientro = ''
    inPrestito = False
    for prestito in prestiti:
        if prestito.terminato == "No":
            rientro = prestito.rientro.strftime('%d-%m-%Y')
            inPrestito = True

    # Controlli per impostare il paragrafo informativo
    if libro.copie == 1 and not inPrestito:
        # Caso 1: 1 copia e non è in prestito
        copie = "Attualmente è disponibile solo una copia di questo libro."
    elif libro.copie == 0 and not inPrestito:
        # Caso 2: 0 copie e non è in prestito
        copie = "Al momento non abbiamo copie disponibili di questo libro."
    elif inPrestito and libro.copie > 0:
        # Caso 3: E' in prestito, ma c'è almeno una copia disponibile
        copie = "Il libro è attualmente in prestito, ma ci sono altre copie disponibili. La data di rientro prevista è: " + rientro
    elif inPrestito:
        # Caso 4: E' in prestito
        copie = "Il libro è attualmente in prestito e non ci sono altre copie disponibili. La data di rientro prevista è: " + rientro
    else:
        # Caso 5: Ci sono <num> copie
        copie = "Sono disponibili " + str(libro.copie) + " copie di questo libro."

    return render_template('libro_show.html', libro = libro, copie = copie, rientro = rientro, testo = testo)

# Stampa della scheda di un Libro
@app.route('/libro/<int:libro_id>/pdf')
@login_required
def scheda_libro(libro_id):
    # Query
    libro = db.session.get(Libro, libro_id)
    libro.download += 1
    db.session.commit()
    # Conversione
    html_string = render_template('libro_scheda.html', libro = libro)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Aggiunta di un Libro
@app.route('/libro/create', methods=['GET', 'POST'])
@login_required
def libro_create():
    if request.method == 'POST':
        # Recupero i parametri 
        nuovo = Libro(
            titolo = request.form['titolo'],
            anno = request.form['anno'],
            classificazione = request.form['classificazione'],
            posizione = request.form['posizione'],
            autore = request.form['autore'],
            genere = request.form['genere'],
            collana = request.form['collana'],
            editore = request.form['editore'],
            note = request.form['note'],
            copie = request.form['copie'],
            disponibile = request.form['disponibile'],
            libro_mese = request.form['libro_mese'],
            rivista = request.form['rivista']
        )
        # Aggiungo al DB
        db.session.add(nuovo)
        db.session.commit()
        
        return redirect(url_for('libro_index'))
    
    return render_template('libro_create.html')

# Modifica di un Libro
@app.route('/libro/<int:libro_id>/edit', methods=['GET', 'POST'])
@login_required
def libro_edit(libro_id):
    libro = Libro.query.get(libro_id)
    if request.method == 'POST':
        # Aggiorno gli attributi
        libro.titolo = request.form['titolo']
        libro.anno = request.form['anno']
        libro.classificazione = request.form['classificazione']
        libro.posizione = request.form['posizione']
        libro.autore = request.form['autore']
        libro.genere = request.form['genere']
        libro.collana = request.form['collana']
        libro.editore = request.form['editore']
        libro.note = request.form['note']
        libro.copie = request.form['copie']
        libro.disponibile = request.form['disponibile']
        libro.libro_mese = request.form['libro_mese']
        libro.rivista = request.form['rivista']
        # Aggiorno nel DB
        db.session.commit()
        
        return redirect(url_for('libro_index'))
    
    return render_template('libro_edit.html', libro = libro)

# Eliminazione di un Libro
@app.route('/libro/<int:libro_id>/delete', methods=['POST'])
@login_required
def libro_delete(libro_id):
    libro = Libro.query.get(libro_id)
    if libro is None:
        return "Libro non trovato", 404
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for('libro_index'))

# Modifica del Genere
@app.route('/libro/<genere>/modifica', methods=['POST'])
@login_required
def modifica_genere(genere):
    if request.method == 'POST':
        # Recupero il genere
        nuovo = request.form.get('genere')
        # Query
        libri = Libro.query.filter_by(genere = genere).all()
        # Aggiornamento in cascata
        for libro in libri:
            libro.genere = nuovo
        db.session.commit()
        
        return redirect(url_for('libro_index'))

# Annullamento del campo Rivista
@app.route('/imposta_no')
@login_required
def imposta_no():
    # Query
    libri = Libro.query.all()
    # Aggiornamento
    for libro in libri:
        libro.rivista = "No"
    db.session.commit()
    
    return redirect(url_for('libro_index'))

# Impostazione delle riviste
@app.route('/imposta_si')
@login_required
def imposta_si():
    # Query
    libri = Libro.query.filter(Libro.genere.like("%ivista%")).all()
    for libro in libri:
        libro.rivista = "Si"
    db.session.commit()
    
    return redirect(url_for('libro_index'))

# Index dei Prestiti
@app.route('/prestiti')
@login_required
def index():
    # Query 
    testo = Testo.query.filter_by(posizione = 'prestito_index').first()
    if current_user.ruolo == "Socio":
        prestiti = Prestito.query.filter_by(utente_id = current_user.id).all()
    else:
        prestiti = Prestito.query.all()
    # Calcolo i giorni restanti
    days_remaining = {}
    for prestito in prestiti:
        if prestito.terminato == "Si":
            # Se è terminato, metto la data
            days_remaining[prestito.id] = prestito.rientro.strftime('%d-%m-%Y')
        else:
            # Se è ancora attivo, i giorni mancanti
            oggi = datetime.today().date()
            fine = prestito.rientro
            days_remaining[prestito.id] = math.ceil((fine - oggi).days)
    
    return render_template('prestito_index.html', prestiti = prestiti, days_remaining = days_remaining, testo = testo)

# Stampa dei prestiti (Socio)
@app.route('/prestiti/pdf')
@login_required
def prestiti_pdf():
    # Query
    prestiti = Prestito.query.filter_by(utente_id = current_user.id).all()
    # Conversione
    html_string = render_template('prestito_pdf.html', prestiti = prestiti)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Stampa dei prestiti (Admin)
@app.route('/prestiti/admin/pdf')
@login_required
def prestiti_admin_pdf():
    # Query
    prestiti = Prestito.query.all()
    # Conversione
    html_string = render_template('prestito_admin_pdf.html', prestiti = prestiti)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    suggestions = []
    if query:
        books = Libro.query.filter(Libro.titolo.ilike(f'%{query}%')).all()
        suggestions = [book.titolo for book in books]
    return jsonify(suggestions)

# Aggiunta di un prestito
@app.route('/prestito/create', methods=['GET', 'POST'])
@login_required
def create_prestito():
    if request.method == 'POST':
        titolo = request.form.get('titolo')
        # Query
        uscita = datetime.strptime(request.form.get('uscita'), '%Y-%m-%d')
        libro = Libro.query.filter(Libro.titolo.like('%' + titolo + '%')).first()
        if libro is None:
            return "Libro non trovato", 404
        rientro = uscita + timedelta(days = 30 if libro.rivista == 'No' else 15)
        # Impostazione del prestito
        prestito = Prestito(
            uscita = uscita,
            rientro = rientro,
            terminato = 'No',
            prorogato = 'No',
            libro_id = libro.id,
            utente_id = current_user.id
        )
        db.session.add(prestito)
        libro.copie -= 1
        if libro.copie == 0:
            libro.disponibile = 'No'
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('prestito_create.html')

# Estensione del prestito
@app.route('/prestito/<int:prestito_id>/extend')
@login_required
def extend(prestito_id):
    prestito = db.session.get(Prestito, prestito_id)
    if prestito.prorogato == "Si":
        flash('Il prestito per il libro "{}" è stato già prorogato.'.format(prestito.libro.titolo), 'error')
        return redirect(url_for('index'))
    # Proroga
    prestito.rientro = prestito.rientro + timedelta(days=15)
    prestito.terminato = "No"
    prestito.prorogato = "Si"
    db.session.commit()

    return redirect(url_for('index'))

# Rotta Terminazione Prestito
@app.route('/prestito/<int:prestito_id>/termina')
@login_required
def termina(prestito_id):
    prestito = db.session.get(Prestito, prestito_id)
    prestito.terminato = "Si"
    prestito.rientro = date.today()
    libro = db.session.get(Libro, prestito.libro_id)
    libro.copie += 1
    if libro.copie > 0:
        libro.disponibile = "Si"
    db.session.commit()
    
    return redirect(url_for('index'))

# Rotta Delete Prestito
@app.route('/prestito/<int:prestito_id>/delete', methods=['POST'])
@login_required
def prestito_delete(prestito_id):
    prestito = db.session.get(Prestito, prestito_id)
    if prestito is None:
        return "Prestito non trovato", 404
    libro = db.session.get(Libro, prestito.libro_id)
    if libro is None:
        return "Libro non trovato", 404
    if prestito.terminato == 'No':
        libro.copie += 1
        if libro.copie > 0:
            libro.disponibile = 'Si'
    db.session.delete(prestito)
    db.session.commit()
    
    return redirect(url_for('index'))

class Corso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    programma = db.Column(db.Text, nullable=False)
    docente = db.Column(db.String(255), nullable=False)
    giorno = db.Column(db.String(255), nullable=False)
    lezioni = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    partenza = db.Column(db.Date)
    minimo = db.Column(db.Integer, nullable=False)
    massimo = db.Column(db.Integer, nullable=False)
    contributo = db.Column(db.Numeric(5,2), nullable=False)
    tessera = db.Column(db.Numeric(5,2), nullable=False)
    prenotazioni = db.Column(db.Integer, nullable=False)
    iscrizioni = db.Column(db.Integer, nullable=False)
    viste = db.Column(db.Integer, default=0)

class Prenotazioni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(255), nullable=False)
    corso_id = db.Column(db.Integer, db.ForeignKey('corso.id'), nullable=False)
    utente_id = db.Column(db.Integer, db.ForeignKey('utente.id'), nullable=False)

    corso = db.relationship('Corso', backref=db.backref('prenotazioni_corso', lazy=True))
    utente = db.relationship('Utente', backref=db.backref('prenotazioni_utente', lazy=True))

# Index dei Corsi
@app.route('/corsi')
def corso_index():
    if current_user.is_authenticated:
        corsi = Corso.query.all()
        testo = Testo.query.filter_by(posizione = 'corso_index').first()
        for corso in corsi:
            corso.posti_rimasti = corso.massimo - corso.prenotazioni        
        # Statistiche
        total_view = db.session.query(db.func.sum(Corso.viste)).scalar() or 0
        top_courses = Corso.query.order_by(Corso.viste.desc()).limit(3).all()
        stats = {
            'total_views': total_view,
            'top_courses': top_courses,
        }

        return render_template('corso_index.html', corsi = corsi, testo = testo, stats = stats)
    else:
        corsi = Corso.query.all()
        testo = Testo.query.filter_by(posizione = 'corso_index').first()
        
        return render_template('corso_non_loggato.html', corsi = corsi, testo = testo)

# Incrementa Visite al corso
@app.route('/corso/<int:corso_id>/incrementa_visite', methods=['POST'])
def incrementa_visite(corso_id):
    corso = db.session.get(Corso, corso_id)
    if corso:
        corso.viste += 1
        db.session.commit()
    return '', 204

# Stampa i corsi
@app.route('/corsi/pdf')
@login_required
def corsi_pdf():
    corsi = Corso.query.all()
    html_string = render_template('corso_pdf.html', corsi = corsi)
    pdf_path = convert_html_to_pdf(html_string)
    return send_file(pdf_path, as_attachment=True)

# Aggiunta di un corso
@app.route('/corso/create', methods=['GET', 'POST'])
@login_required
def corso_create():
    if request.method == 'POST':
        
        nuovo = Corso(
            nome = request.form['nome'],
            programma = request.form['programma'],
            docente = request.form['docente'],
            giorno = request.form['giorno'],
            lezioni = request.form['lezioni'],
            note = request.form['note'],
            partenza = request.form['partenza'],
            minimo = request.form['minimo'],
            massimo = request.form['massimo'],
            contributo = request.form['contributo'],
            tessera = request.form['tessera'],
            prenotazioni = request.form['prenotazioni'],
            iscrizioni = request.form['iscrizioni']
        )
        db.session.add(nuovo)
        db.session.commit()
        
        return redirect(url_for('corso_index'))
    
    return render_template('corso_create.html')

# Modifica di un Corso
@app.route('/corso/<int:corso_id>/edit', methods=['GET', 'POST'])
@login_required
def corso_edit(corso_id):
    corso = db.session.get(Corso, corso_id)
    if request.method == 'POST':
        
        corso.nome = request.form['nome'],
        corso.programma = request.form['programma'],
        corso.docente = request.form['docente'],
        corso.giorno = request.form['giorno'],
        corso.lezioni = request.form['lezioni'],
        corso.note = request.form['note'],
        partenza = request.form['partenza'],
        if partenza == '':
            partenza = None
        corso.partenza = partenza        
        corso.minimo = request.form['minimo'],
        corso.massimo = request.form['massimo'],
        corso.contributo = request.form['contributo'],
        corso.tessera = request.form['tessera'],
        corso.prenotazioni = request.form['prenotazioni'],
        corso.iscrizioni = request.form['iscrizioni']
        db.session.commit()
        
        return redirect(url_for('corso_index'))
    
    return render_template('corso_edit.html', corso = corso)

# Eliminazione di un corso
@app.route('/corso/<int:corso_id>/delete', methods=['POST'])
@login_required
def corso_delete(corso_id):
    corso = Corso.query.get(corso_id)
    if corso is None:
        return "Corso non trovato", 404
    db.session.delete(corso)
    db.session.commit()
    
    return redirect(url_for('corso_index'))

# Index prenotazione
@app.route('/prenotazioni')
@login_required
def booking_index():
    titolo = ""
    if current_user.ruolo == "Socio":
        prenotazioni = Prenotazioni.query.filter_by(utente_id = current_user.id).all()
        titolo = "I Miei Percorsi Formativi - " + current_user.nome
    else:
        prenotazioni = Prenotazioni.query.all()
        titolo = "Panoramica delle Prenotazioni ai Corsi"
    # Raggruppa le prenotazioni per corso
    prenotazioni_per_corso = {}
    for prenotazione in prenotazioni:
        if prenotazione.corso_id not in prenotazioni_per_corso:
            prenotazioni_per_corso[prenotazione.corso_id] = []
        prenotazioni_per_corso[prenotazione.corso_id].append(prenotazione)

    testo = Testo.query.filter_by(posizione = 'prenotazione_index').first()
    
    return render_template('prenotazioni_index.html', prenotazioni_per_corso = prenotazioni_per_corso, titolo = titolo, testo = testo)

@app.route('/suggerimento', methods=['GET'])
def suggerimento():
    query = request.args.get('query', '')
    suggestions = []
    if query:
        corsi = Corso.query.filter(Corso.nome.like(f'%{query}%')).all()
        suggestions = [corso.nome for corso in corsi]
    return jsonify(suggestions)

# Aggiunta di una prenotazione
@app.route('/prenotazione/create', methods=['GET', 'POST'])
@login_required
def create_prenotazione():
    error = ""
    nome = ""
    if request.method == 'POST':
        nome = request.form.get('nome')
        corso = Corso.query.filter(Corso.nome.like('%' + nome + '%')).first()
        if corso is None:
            error = "Corso non trovato"
        else:
            prenotazione = Prenotazioni(
                stato = "Prenotato",
                corso_id = corso.id,
                utente_id = current_user.id
            )
            db.session.add(prenotazione)
            corso.prenotazioni += 1  # incrementa il contatore delle prenotazioni
            db.session.commit()
            
            return redirect(url_for('booking_index'))
    
    return render_template('prenotazioni_create.html', error = error, nome = nome)

# Eliminazione di una prenotazione
@app.route('/prenotazione/<int:prenotazione_id>/delete', methods=['POST'])
@login_required
def prenotazione_delete(prenotazione_id):
    prenotazione = db.session.get(Prenotazioni, prenotazione_id)
    if prenotazione is None:
        return "Prenotazione non trovata", 404
    corso = db.session.get(Corso, prenotazione.corso_id)
    if corso is None:
        return "Corso non trovato", 404
    if prenotazione.stato == 'Prenotato':
        corso.prenotazioni -= 1
    else: 
        corso.iscrizioni -= 1
    db.session.delete(prenotazione)
    db.session.commit()
    
    return redirect(url_for('booking_index'))

# Conferma prenotazione
@app.route('/prenotazione/<int:prenotazione_id>/conferma', methods=['GET'])
@login_required
def conferma_prenotazione(prenotazione_id):
    prenotazione = db.session.get(Prenotazioni, prenotazione_id)
    if prenotazione is None:
        return "Prenotazione non trovata", 404
    prenotazione.stato = "Iscritto"
    db.session.commit()
    corso = db.session.get(Corso, prenotazione.corso_id)
    if corso is not None:
        corso.prenotazioni -= 1
        corso.iscrizioni += 1
        db.session.commit()
    
    return redirect(url_for('booking_index'))

# Stampa prenotazione (Socio)
@app.route('/prenotazione/<corso_id>/pdf')
@login_required
def prenotazione_pdf(corso_id):
    prenotazioni = Prenotazioni.query.filter_by(corso_id = corso_id).all()
    html_string = render_template('prenotazioni_pdf.html', prenotazioni = prenotazioni)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Stampa prenotazioni (Admin)
@app.route('/prenotazioni/<corso_id>/pdf')
@login_required
def prenotazione_admin_pdf(corso_id):
    prenotazioni = Prenotazioni.query.filter_by(corso_id = corso_id).all()
    html_string = render_template('prenotazioni_admin_pdf.html', prenotazioni = prenotazioni)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Index Utenti
@app.route('/utenti', methods=['GET'])
@login_required
def index_utente():
    utenti = Utente.query.all()
    for utente in utenti:
        utente.prestiti_count = Prestito.query.filter_by(utente_id=utente.id).count()
        utente.prenotazioni_count = Prenotazioni.query.filter_by(utente_id=utente.id).count()
    return render_template('utente_index.html', utenti = utenti)

# Modifica utente, inutilizzata
@app.route('/utente/<int:utente_id>/edit', methods=['GET', 'POST'])
@login_required
def utente_edit(utente_id):
    utente = db.session.get(Utente, utente_id)
    if request.method == 'POST':
        utente.email = request.form['email'],
        utente.telefono = request.form['telefono']

        db.session.commit()
        return redirect(url_for('index_utente'))
    
    return render_template('utente_edit.html', utente = utente)

# Stampa degli utenti
@app.route('/utenti/pdf')
@login_required
def utente_pdf():
    utenti = Utente.query.all()
    for utente in utenti:
        utente.prestiti_count = Prestito.query.filter_by(utente_id=utente.id).count()
        utente.prenotazioni_count = Prenotazioni.query.filter_by(utente_id=utente.id).count()
    html_string = render_template('utente_pdf.html', utenti = utenti)
    pdf_path = convert_html_to_pdf(html_string)
    
    return send_file(pdf_path, as_attachment=True)

# Gruppo di lettura
@app.route('/gruppo_lettura')
@login_required
def gruppo_lettura():
    month = Libro.query.filter_by(libro_mese = 'Si').first()
   
    return render_template('gruppo_lettura.html', month = month)

if __name__ == '__main__':
    app.run()