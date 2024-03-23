from flask import Flask, render_template, redirect, make_response, request, session, abort
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from data import db_session
from data.users import User
from data.news import News
from data.birthday import Birthday
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.news import NewsForm
from forms.birthday import BDaysForm
import datetime
from waitress import serve

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=20
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager(app)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/test')
def test():
    return "test"


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/note")
def note():
    db_sess = db_session.create_session()
    # news = db_sess.query(News).filter(News.is_private != True)

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("note.html", news=news)


@app.route("/birthday")
def birthday():
    db_sess = db_session.create_session()
    bdays = db_sess.query(Birthday)

    return render_template("birthday.html", bdays=bdays)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        # news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление заметки',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/note')


@app.route('/bdays_delete/<int:id>', methods=['GET', 'POST'])
def bdays_delete(id):
    db_sess = db_session.create_session()
    bdays = db_sess.query(Birthday).filter(Birthday.id == id,
                                           ).first()
    if bdays:
        db_sess.delete(bdays)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/birthday')


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            # form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            # news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование заметки',
                           form=form
                           )


@app.route('/bdays/<int:id>', methods=['GET', 'POST'])
def edit_bdays(id):
    form = BDaysForm()
    # if request.method == "GET":
    db_sess = db_session.create_session()
    bdays = db_sess.query(Birthday).filter(Birthday.id == id).first()
    print(bdays.dt)
    if bdays:
        form.fio.data = bdays.fio
        form.dt.data = bdays.dt
    else:
        abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        bdays = db_sess.query(Birthday).filter(Birthday.id == id
                                               ).first()
        if bdays:
            # news.title = form.title.data
            bdays.fio = form.fio.data
            bdays.dt = form.dt.data
            db_sess.commit()
            return redirect('/birthday')
        else:
            abort(404)
    return render_template('birthday.html',
                           title='Редактирование дня рождения',
                           form=form
                           )


def main():
    db_session.global_init("BD/assistant.db")  # "db/assistant.db"
    #url = "https://www.pythonanywhere.com/user/KatySidorova/files/home/KatySidorova/DB/assistant.db"
    #url = "https:\\\\www.pythonanywhere.com\\user\\KatySidorova\\files\\home\\KatySidorova\\DB\\assistant.db"
    #db_session.global_init(url)

    # app.run(port=8081, host='127.0.0.1')
    serve(app, port=8081, host='127.0.0.1')


if __name__ == '__main__':
    main()
