from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

# Criação do banco de dados
with app.app_context():
    db.create_all()

@app.route('/')
def inicio():
    return render_template("inicio.html")

@app.route('/contatos')
def contatos():
    return render_template("contatos.html")

@app.route('/acesso')
def acesso():
    return render_template("acesso.html")

@app.route('/criarconta', methods=['GET', 'POST'])
def criarconta():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Primeiro Verificar se o usuário já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Email já existe!')
            return redirect(url_for('criarconta'))

        #então cria um novo

        # Criar um novo usuário - verifica se as variáveis nome, email e senha existem
        if nome and email and senha:
            try:
                senha_hash = generate_password_hash(senha)
                novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
                db.session.add(novo_usuario)
                db.session.commit() #é usado para salvar as mudanças feitas na sessão atual do banco de dados.
                flash('Usuário criado com sucesso!')

                return redirect(url_for('acesso'))

            except Exception as e:
                db.session.rollback()  # Reverte a sessão em caso de erro
                flash(f'Erro ao criar usuário: {e}')
                return redirect(url_for('criarconta'))

    return render_template('criarconta.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email).first()

        # Verificação das credenciais
        if usuario and check_password_hash(usuario.senha, senha):
            return redirect(url_for('inicio'))  # Redirecionar para a página inicial
        else:
            flash('Usuário ou senha incorretos!')

    return render_template('acesso.html')

if __name__ == '__main__':
    app.run(debug=True)
