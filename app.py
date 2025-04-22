from flask import Flask, request, render_template, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

DB_URL = os.environ.get("DB_URL", "sqlite:///jobs.db")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    job_title = Column(String(255))
    experience = Column(String(255))
    salary = Column(String(255))     
    description = Column(Text)
    creator_user = Column(String(255))

Base.metadata.create_all(engine)

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
        creator_user=data.get("creator_user")
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
