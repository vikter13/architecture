## basic
from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

## forms for auth
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError 

## session
from flask import session

## crypt
from flask_bcrypt import Bcrypt


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///themplace.db'
app.config['SECRET_KEY'] = 'vikter&roma'

API_KEY = "9dffeb17-0460-4f39-a421-7ab0b194a2ce"

db = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # если пользователь попытается получить доступ к странице без аутентификации, то его перекинет на login

@login_manager.user_loader # запоминает id user'а для сессии
def load_user(user_id):
    return Users.query.get(int(user_id))



## classes

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.Text, nullable=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class Places(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class registerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})
    password = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Register")

    def validate_username(self, username): # check if username exist
        existing_user_username = Users.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')
        
class loginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "username"})
    password = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "password"})
    submit = SubmitField("Login")

## main part ------------------------------------------

@app.route('/')
def home():
    places = Places.query.all()
    place = Places.query.first()

    if place:
        longitude, latitude = place.longitude, place.latitude
        coordinates = f'{longitude},{latitude}'
        name = place.name
    else:
        coordinates = '37.620070,55.753630'
        name = 'Москва'

    API_KEY = "9dffeb17-0460-4f39-a421-7ab0b194a2ce"

    return render_template('home.html',
                           coordinates=coordinates,
                           API_KEY=API_KEY,
                           name=name,
                           places=places)

@app.route('/')
@login_required
def index():
    user = current_user

    if user.is_authenticated and user.places:
        place = user.places[0]

        longitude, latitude = map(float, place.coordinates.split(','))
        coordinates = f'{longitude},{latitude}'
        name = place.name
    else:
        coordinates = '37.620070,55.753630'
        name = 'Москва'


    return render_template('index.html',
                           coordinates=coordinates,
                           API_KEY=API_KEY,
                           name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('mainwindow'))

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/mainwindow', methods=['GET', 'POST'])
@login_required
def mainwindow():
    return render_template('mainwindow.html')


@app.route('/add_place', methods=['POST'])
@login_required
def add_place():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    name = request.form['name']
    new_place = Places(latitude=latitude, longitude=longitude, name=name, user_id=current_user.id)
    db.session.add(new_place)
    db.session.commit()
    return redirect(url_for('mainwindow'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registerForm()

    if form.validate_on_submit(): # возвращает True, если форма была отправлена методом POST и прошла все проверки валидации
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Users(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/visits')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    
    count_visit = session['visits']

    return render_template('/visits.html', count_visit=count_visit)


@app.route('/search_places')
def search_places():
    query = request.args.get('query')

    places = Places.query.filter(Places.name.lower().ilike(f'%{query}%')).all()
    print(places)
    places_data = [{'name': place.name, 'latitude': place.latitude, 'longitude': place.longitude} for place in places]
    print(places_data)
    response_data = {'places': places_data, 'API_KEY': "9dffeb17-0460-4f39-a421-7ab0b194a2ce"}

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)


    # from app import db
    # db.create_all()
    #
    # # Создаем объекты пользователей
    # user1 = Users(full_name='Виктор Теняев', username='vikter',
    #               password='$2b$12$QgxzlEDpSjN1a/GkK2iCf.ptV6SrxRw4O80uWVZkIegAi140UfJCm')
    # user2 = Users(full_name='Рамазан Наврузов', username='roma',
    #               password='$2b$12$QgxzlEDpSjN1a/GkK2iCf.ptV6SrxRw4O80uWVZkIegAi140UfJCm')
    #
    # # Создаем объекты мест
    # place1 = Places(latitude=55.751188, longitude=37.627940, name='Парк "Зарядье"', user_id=user1.id)
    # place2 = Places(latitude=55.718356, longitude=37.591445, name='Парк "Нескучный Сад"', user_id=user1.id)
    # place3 = Places(latitude=55.790492, longitude=37.531372, name='Торговый центр "Авиапарк"', user_id=user2.id)
    #
    # db.session.add(user1)
    # db.session.add(user2)
    #
    # db.session.commit()
    # db.session.add(place1)
    # db.session.add(place2)
    # db.session.add(place3)
    #
    # db.session.commit()





