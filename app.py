from flask import Flask, request, render_template, jsonify, Response
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import wraps
import os

app = Flask(__name__)

DB_URL = "sqlite:///jobs.db"
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    job_title = Column(String(255))
    experience = Column(String(255))
    salary = Column(String(255))
    description = Column(Text)
    creator_user = Column(String(255))


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USER or auth.password != ADMIN_PASS:
            return Response(
                "Could not verify your access level.\n"
                "You have to login with proper credentials",
                401,
                {"WWW-Authenticate": 'Basic realm="Login Required"'},
            )
        return f(*args, **kwargs)

    return decorated


@app.route("/admin/init_db", methods=["POST"])
@requires_auth
def init_db():
    Base.metadata.create_all(engine)
    return jsonify({"message": "Database initialized"}), 200


@app.route("/admin/reset_db", methods=["POST"])
@requires_auth
def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return jsonify({"message": "Database reset"}), 200


@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    job = Job(
        job_title=data.get("job_title"),
        experience=data.get("experience"),
        salary=data.get("salary"),
        description=data.get("description"),
        creator_user=data.get("creator_user"),
    )

    db = Session()
    db.add(job)
    db.commit()
    db.close()

    return jsonify({"message": "Job saved successfully"}), 201


@app.route("/jobs", methods=["GET"])
def list_jobs():
    db = Session()
    jobs = db.query(Job).all()
    db.close()
    return render_template("jobs.html", jobs=jobs)


@app.route("/")
def home():
    return "Job Posting API is running!"
