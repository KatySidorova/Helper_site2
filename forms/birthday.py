from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField


class BDaysForm(FlaskForm):
    fio = TextAreaField('ФИО')
    dt = TextAreaField("Дата рождения")
    submit = SubmitField('Применить')
