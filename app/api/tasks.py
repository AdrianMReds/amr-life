import os

from fastapi import APIRouter, HTTPException, Header, status, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import date
from enum import Enum

from app.core.database import get_db_client
from app.api.auth import verificar_token
from app.core.constants import TASK_TYPES_DICT, TASK_PRIORITIES_DICT, TASK_STATUS_DICT, TASK_REMINDER_DICT

load_dotenv()

router = APIRouter(prefix="/tasks")

TaskPriority = Enum("TaskPriority", {k: v for k, v in TASK_PRIORITIES_DICT.items()}, type=str)
TaskType = Enum("TaskType", {k: v for k, v in TASK_TYPES_DICT.items()}, type=str)
TaskStatus = Enum("TaskStatus", {k: v for k, v in TASK_STATUS_DICT.items()}, type=str)
TaskReminder = Enum("TaskReminder", {k: v for k, v in TASK_REMINDER_DICT.items()}, type=str)

class Task(BaseModel):
    name:str
    description: str
    priority: TaskPriority
    deadline: date #Enviar desde cliente como "2026-12-31"
    type: TaskType
    status: TaskStatus
    reminder: TaskReminder

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_tarea(task: Task, usuario: dict = Depends(verificar_token)):
    try:
        with get_db_client() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, name, description, priority, deadline, task_type, status, reminder) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (usuario["id"], task.name, task.description, task.priority, task.deadline, task.type, task.status, task.reminder))
        return {"message": "Tarea creada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_tasks(usuario: dict = Depends(verificar_token)):
    try:
        with get_db_client() as cur:
            cur.execute("SELECT * FROM tasks WHERE user_id = %s", (usuario["id"],))
            tasks = cur.fetchall()
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}")
def get_task(task_id: int, usuario: dict = Depends(verificar_token)):
    try:
        with get_db_client() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
def update_task(task_id: int, task: Task, usuario: dict = Depends(verificar_token)):
    try:
        with get_db_client() as cur:
            cur.execute("""
                UPDATE tasks SET name = %s, description = %s, priority = %s, deadline = %s, task_type = %s, status = %s, reminder = %s WHERE id = %s
            """, (task.name, task.description, task.priority, task.deadline, task.type, task.status, task.reminder, task_id))
        return {"message": "Tarea actualizada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
def delete_task(task_id: int, usuario: dict = Depends(verificar_token)):
    try:
        with get_db_client() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        return {"message": "Tarea eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
