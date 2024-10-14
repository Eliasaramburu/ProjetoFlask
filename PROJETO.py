from flask import Flask, render_template, request, redirect, url_for, flash
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Pasta onde as fotos serão salvas

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    foto_perfil = db.Column(db.String(150), nullable=True)

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

        # Verificar se o usuário já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Email já existe!')
            return redirect(url_for('criarconta'))

        # Criar um novo usuário
        if nome and email and senha:
            try:
                senha_hash = generate_password_hash(senha)

                novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Usuário criado com sucesso!')

                return redirect(url_for('acesso'))

            except Exception as e:
                db.session.rollback()
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
            return redirect(url_for('perfil', user_id=usuario.id))  # Passar o ID do usuário
        else:
            flash('Usuário ou senha incorretos!')

    return render_template('acesso.html')

@app.route('/perfil/<int:user_id>', methods=['GET', 'POST'])
def perfil(user_id):
    usuario = Usuario.query.get_or_404(user_id)

    if request.method == 'POST':
        foto_perfil = request.files.get('foto_perfil')

        if foto_perfil:
            foto_caminho = os.path.join(app.config['UPLOAD_FOLDER'], foto_perfil.filename)
            foto_perfil.save(foto_caminho)

            # Atualiza o caminho da foto no banco de dados
            usuario.foto_perfil = foto_caminho
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!')

    return render_template('perfil.html', usuario=usuario)


if __name__ == '__main__':
    app.run(debug=True)
