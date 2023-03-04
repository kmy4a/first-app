from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, DateTime, Boolean
import os
import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


class examName(db.Model):
    __tablename__ = "exam_name"
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String, nullable=False)


class Exams(db.Model):
    __tablename__ = "exams"
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(Integer, ForeignKey(examName.id))
    amount = db.Column(Integer, nullable=False)
    date = db.Column(DateTime, nullable=False)
    result = db.Column(Boolean, nullable=True)


@app.route("/")
def root():
    exams = []
    name = ""
    r = db.session.query(Exams)
    for exam in r:
        er = db.session.query(examName).filter(examName.id == exam.exam_id)
        for e in er:
            result = e

        if result is not None:
            name = result.name

        if exam.amount is None:
            exam.amount = 0
        examDate = exam.date
        examDate = datetime.date(examDate.year, examDate.month, examDate.day)

        now = datetime.datetime.now()
        remain = (examDate - datetime.date(now.year, now.month, now.day)).days

        summary = {
            "id": exam.id,
            "name": name,
            "date": examDate,
            "remain": remain,
            "amount": str(exam.amount) + "H",
            "result": exam.result
        }
        exams.append(summary)

    return render_template("index.html", exams=exams)


@app.route("/add/", methods=["GET"])
def get_add():
    return render_template("add.html")


@app.route("/add/", methods=["POST"])
def post_add():
    name = request.form["examName"]
    datestr = request.form["examDate"]
    exams = db.session.query(examName).filter(examName.name == name)
    result = False
    for exam in exams:
        if exam.name is not None:
            result = True

    if not result:
        tmp = examName()
        tmp.name = name
        db.session.add(tmp)
        db.session.commit()

    tmp = Exams()
    exams = db.session.query(examName).filter(examName.name == name)
    result = False
    for exam in exams:
        if exam.name is not None:
            tmp.exam_id = exam.id
    tmp.amount = 0
    tdatetime = datetime.datetime.strptime(datestr, "%Y-%m-%d")
    tmp.date = tdatetime
    db.session.add(tmp)
    db.session.commit()
    return redirect("/")


@app.route("/update/<int:id>", methods=["GET"])
def get_update(id):
    fallbackURL = "/update/" + str(id)
    return render_template("update.html", url=fallbackURL)


@app.route("/update/<int:id>", methods=["POST"])
def post_update(id):
    achieve = int(request.form["achieve"])
    targetExam = db.session.query(Exams).filter(Exams.id == id).first()
    amount = targetExam.amount + achieve
    targetExam.amount = amount
    db.session.commit()
    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    db.session.query(Exams).filter(Exams.id == id).delete()
    db.session.commit()
    return redirect("/")


@app.route("/result/<int:id>", methods=["GET"])
def get_result(id):
    return render_template("result.html", id=id)


@app.route("/result/<int:id>", methods=["POST"])
def post_result(id):
    result = request.form.get("radio")
    targetExam = db.session.query(Exams).filter(Exams.id == id).first()
    if result == "pass":
        targetExam.result = True
    elif result == "failure":
        targetExam.result = False
    else:
        pass

    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    if not os.path.exists("instance/database.db"):
        with app.app_context():
            db.create_all()
    app.run()
