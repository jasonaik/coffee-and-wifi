from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///cafes.db")
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    Integer: Callable
    String: Callable


db = MySQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250), unique=True, nullable=False)
    img_url = db.Column(db.String(250), unique=True, nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Integer, nullable=False)
    has_toilet = db.Column(db.Integer, nullable=False)
    has_wifi = db.Column(db.Integer, nullable=False)
    can_take_calls = db.Column(db.Integer, nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)


db.create_all()


class CafeForm(FlaskForm):
    cafe = StringField('Cafe Name', validators=[DataRequired()])
    map_url = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    img_url = StringField('Cafe Image (URL)', validators=[DataRequired(), URL()])
    location = StringField('Location Name', validators=[DataRequired()])
    has_sockets = SelectField('Sockets', choices=["Yes", "No"],
                              validators=[DataRequired()])
    has_toilet = SelectField('Toilets', choices=["Yes", "No"],
                             validators=[DataRequired()])
    has_wifi = SelectField('Wi-Fi', choices=["Yes", "No"],
                           validators=[DataRequired()])
    can_take_calls = SelectField('Calls', choices=["Yes", "No"],
                                 validators=[DataRequired()])
    seats = SelectField('Seats', choices=["0-10", "10-20", "30-40", "40-50", "50+"],
                        validators=[DataRequired()])
    coffee_price = DecimalField('Coffee Price in £')
    submit = SubmitField('Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["POST", "GET"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        if form.has_sockets.data == "Yes":
            sockets_yn = 1
        else:
            sockets_yn = 0

        if form.has_sockets.data == "Yes":
            toilet_yn = 1
        else:
            toilet_yn = 0

        if form.has_sockets.data == "Yes":
            wifi_yn = 1
        else:
            wifi_yn = 0

        if form.has_sockets.data == "Yes":
            calls_yn = 1
        else:
            calls_yn = 0

        new_cafe = Cafe(
            name=form.cafe.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=sockets_yn,
            has_toilet=toilet_yn,
            has_wifi=wifi_yn,
            can_take_calls=calls_yn,
            seats=form.seats.data,
            coffee_price=f"£{round(form.coffee_price.data, 2)}"
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
def edit(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe.has_sockets == 1:
        sockets_yn = "Yes"
    else:
        sockets_yn = "No"

    if cafe.has_toilet == 1:
        toilet_yn = "Yes"
    else:
        toilet_yn = "No"

    if cafe.has_wifi == 1:
        wifi_yn = "Yes"
    else:
        wifi_yn = "No"

    if cafe.can_take_calls == 1:
        calls_yn = "Yes"
    else:
        calls_yn = "No"
    edit_form = CafeForm(
        cafe=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        has_sockets=sockets_yn,
        has_toilet=toilet_yn,
        has_wifi=wifi_yn,
        can_take_calls=calls_yn,
        seats=cafe.seats,
        coffee_price=float(cafe.coffee_price.strip("£"))
    )

    if edit_form.validate_on_submit():
        if edit_form.has_sockets.data == "Yes":
            sockets_yn = 1
        else:
            sockets_yn = 0

        if edit_form.has_toilet.data == "Yes":
            toilet_yn = 1
        else:
            toilet_yn = 0

        if edit_form.has_wifi.data == "Yes":
            wifi_yn = 1
        else:
            wifi_yn = 0

        if edit_form.can_take_calls.data == "Yes":
            calls_yn = 1
        else:
            calls_yn = 0

        cafe.name = edit_form.cafe.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.has_sockets = sockets_yn
        cafe.has_toilet = toilet_yn
        cafe.has_wifi = wifi_yn
        cafe.can_take_calls = calls_yn
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = f"£{round(edit_form.coffee_price.data, 2)}"
        db.session.commit()
        return redirect(url_for("cafes"))

    return render_template("add.html", form=edit_form, is_edit=True)


@app.route('/cafes')
def cafes():
    all_cafes = Cafe.query.all()
    return render_template('cafes.html', cafes=all_cafes)


@app.route("/delete")
def delete_page():
    all_cafes = Cafe.query.all()
    return render_template('delete.html', cafes=all_cafes)


@app.route("/delete/<int:cafe_id>")
def delete(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for("delete_page"))


if __name__ == '__main__':
    app.run(debug=True)
