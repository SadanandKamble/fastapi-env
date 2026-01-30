import asyncio
import uvicorn
import random
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker 

# fastapi setup
app = FastAPI(title="Student management API")

# database setup
DATABASE_URL = "postgresql://user:Sada0001@localhost:5432/studentdb"
engine = create_engine(DATABASE_URL)   
SessionLocal = sessionmaker (bind=engine)

# Pydantic model for student for post request

class Student(BaseModel):
    id: int
    name: str
    score: float


#ASYNC:SIMULATE FETCHING DATA FROM EXTERNAL SOURCE
async def fetch_score(student):
    await asyncio.sleep(1)  # Simulate network delay
    data = {
        "id": random.randint(1, 1000),
        "name": f"Student_{random.randint(1, 100)}",
        "score": str(random.randint(50, 100))
    }
    return data

#main processing function
async def process_student(students):
    #fetch scores aynchronously
    tasks=[fetch_score(s) for s in students]
    scores=await asyncio.gather(*tasks)


#NUMPY:stats  
    scores_array = np.array(scores)
    stats={
            "AVERAGE":float(scores_array.mean()),
            "HIGHEST":int (scores_array.max()),
            "LOWEST":int(scores_array.min())

    }


 #PANDAS : BUILD DATAFRAME
    df= pd.DataFrame({
        "Student": students,
        "Score": scores
    })
    df["Result"] = df["Score"].apply(lambda x: "PASS" if x >= 60 else "FAIL")

    #SAVE CSV
    df.to_csv("students.csv", index=False)

    # save postgresql
    db = SessionLocal()
    for index, row in df.iterrows():    
        stmt = text("INSERT INTO students (id, name, score, result) VALUES (:id, :name, :score, :result)")
        db.execute(stmt, {
            "id": row["id"],
            "name": row["name"],
            "score": row["Score"],
            "result": row["Result"]
        })      
    db.commit()
    db.close()

    return {"stats": stats, "dataframe": df.to_dict(orient="records")}

@app.get("/run")
async def run_simulation():
    students = ["Alice", "Bob", "Charlie", "Diana", "Eve"]  # Example student list
    data ,stats = await process_student(students)
    return {"message": "Data processing completed successfully", "data": data, "stats":stats}


#POST ENDPOINT: TO ADD STUDENT
@app.post("/add_student")
async def add_student(student: Student):

    #load csv or create new one
    try:
        df = pd.read_csv("students.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["id", "name", "score", "result"])
    #calculate result
    result = "PASS" if int(student.score) >= 60 else "FAIL"
    #append to dataframe
    new_row = pd.DataFrame([{
        "id": student.id,
        "name": student.name,
        "score": student.score,
        "result": result
    }])


    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    #save to csv
    df.to_csv("students.csv", index=False)

    #insert into Postgressql
    db = SessionLocal()
    stmt = text("INSERT INTO students (id, name, score, result) VALUES (:id, :name, :score, :result)")
    db.execute(stmt, {
        "id": student.id,               
        "name": student.name,
        "score": student.score,
        "result": result
    })   
    db.commit()
    db.close()

#Recalculate stats
    scores_array = np.array(df["score"].astype(int))
    stats = {
        "AVERAGE": float(scores_array.mean()),
        "HIGHEST": int(scores_array.max()),
        "LOWEST": int(scores_array.min())
    }

    return{
            "message": f"Student {student.name} added successfully",
            "student":new_row.to_dict(orient="records")[0],"stats": stats
           }
