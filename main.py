import asyncio
import random
import numpy as np
import pandas as pd
import uvicorn

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# FastAPI app
app = FastAPI(title="Student management API")

# Database setup
DATABASE_URL = "postgresql://user:Sada0001@localhost:5432/studentdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# Pydantic model for student
class Student(BaseModel):
    id: int
    name: str
    score: float


async def fetch_score(student_name: str) -> dict:
    """Simulate fetching a score for a student (returns dict)."""
    await asyncio.sleep(1)
    return {
        "id": random.randint(1, 1000),
        "name": student_name,
        "score": random.randint(50, 100),
    }


async def process_student(students: list):
    """Fetch scores asynchronously, save to CSV and DB, and return stats + records."""
    tasks = [fetch_score(s) for s in students]
    records = await asyncio.gather(*tasks)

    df = pd.DataFrame(records)
    if df.empty:
        stats = {"AVERAGE": 0.0, "HIGHEST": 0, "LOWEST": 0}
    else:
        df["score"] = df["score"].astype(int)
        df["result"] = df["score"].apply(lambda x: "PASS" if x >= 60 else "FAIL")
        scores_array = df["score"].to_numpy()
        stats = {
            "AVERAGE": float(scores_array.mean()),
            "HIGHEST": int(scores_array.max()),
            "LOWEST": int(scores_array.min()),
        }

    df.to_csv("students.csv", index=False)

    db = SessionLocal()
    for _, row in df.iterrows():
        stmt = text(
            "INSERT INTO students (id, name, score, result) VALUES (:id, :name, :score, :result)"
        )
        db.execute(
            stmt,
            {"id": int(row["id"]), "name": row["name"], "score": int(row["score"]), "result": row["result"]},
        )
    db.commit()
    db.close()

    return {"stats": stats, "dataframe": df.to_dict(orient="records")}


@app.get("/run")
async def run_simulation():
    students = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    result = await process_student(students)
    return {"message": "Data processing completed successfully", "result": result}


@app.post("/add_student")
async def add_student(student: Student):
    try:
        df = pd.read_csv("students.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["id", "name", "score", "result"])

    result = "PASS" if int(student.score) >= 60 else "FAIL"
    new_row = pd.DataFrame([{"id": int(student.id), "name": student.name, "score": int(student.score), "result": result}])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("students.csv", index=False)

    db = SessionLocal()
    stmt = text(
        "INSERT INTO students (id, name, score, result) VALUES (:id, :name, :score, :result)"
    )
    db.execute(stmt, {"id": int(student.id), "name": student.name, "score": int(student.score), "result": result})
    db.commit()
    db.close()

    scores_array = df["score"].astype(int).to_numpy()
    stats = {
        "AVERAGE": float(scores_array.mean()),
        "HIGHEST": int(scores_array.max()),
        "LOWEST": int(scores_array.min()),
    }

    return {"message": f"Student {student.name} added successfully", "student": new_row.to_dict(orient="records")[0], "stats": stats}


