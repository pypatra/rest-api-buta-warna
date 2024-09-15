import json
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import AnswerSubmission

app = FastAPI()

session_storage = {}


def load_tests():
    with open("data/data_test_buta_warna.json") as f:
        return json.load(f)


test_buta_warna = load_tests()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session_data(user_id: str):
    if user_id not in session_storage:
        session_storage[user_id] = []
    return session_storage[user_id]


@app.get("/api/tests/start")
def start_test(user_id: str):
    session_storage[user_id] = []
    test_pertama = test_buta_warna[0]
    return {
        "message": "Test session started",
        "next_test": {
            "id": test_pertama["id"],
            "image_url": test_pertama["image_url"],
            "options": test_pertama["options"],
            "description": test_pertama["description"],
        },
    }


@app.post("/api/tests/{test_id}/submit")
def submit_answer(
    test_id: int,
    submission: AnswerSubmission,
    user_id: str,
    session_data: List[dict] = Depends(get_session_data),
):
    test = next((test for test in test_buta_warna if test["id"] == test_id), None)

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    session_data.append({"id": test_id, "answer": submission.answer})

    next_test_index = test_id
    if next_test_index < len(test_buta_warna):
        next_test = test_buta_warna[next_test_index]
        return {
            "message": "Answer submitted",
            "next_test": {
                "id": next_test["id"],
                "image_url": next_test["image_url"],
                "options": next_test["options"],
                "description": next_test["description"],
            },
        }
    else:
        return {
            "message": "Test Selesai",
            "result_url": f"/api/tests/result?user_id={user_id}",
        }


@app.get("/api/tests/result")
def get_result(user_id: str):
    answers = session_storage.get(user_id, [])
    correct_count = 0
    total_tests = len(test_buta_warna)

    for answer_data in answers:
        test_id = answer_data["id"]
        user_answer = answer_data["answer"]
        test = next((test for test in test_buta_warna if test["id"] == test_id), None)

        if test and user_answer == test["correct_answer"]:
            correct_count += 1

    correct_threshold_normal = total_tests * 0.8
    correct_threshold_parsial = total_tests * 0.4

    if correct_count >= correct_threshold_normal:
        jenis_buta_warna = "normal"
    elif correct_count >= correct_threshold_parsial:
        jenis_buta_warna = "buta warna parsial"
    else:
        jenis_buta_warna = "buta warna total"

    return {
        "result": jenis_buta_warna.title(),
        "details": {"correct_count": correct_count, "total_tests": total_tests},
    }
