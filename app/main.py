from fastapi import FastAPI, Depends
from app.auth.dependencies import require_role
from app.nfc.router import router as nfc_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(nfc_router)

@app.get("/health")
def health():
    return {"status": "ok"}

