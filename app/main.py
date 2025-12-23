from fastapi import FastAPI, Depends
from app.auth.dependencies import require_role
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/secure-endpoint")
def secure_endpoint(user=Depends(require_role(["CAREGIVER"]))):
    return {
        "message": "Access granted",
        "user_id": user["user_id"],
        "organization_id": user["organization_id"],
    }

