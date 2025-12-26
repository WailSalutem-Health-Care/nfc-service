from fastapi import FastAPI
from app.nfc.router import router as nfc_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(nfc_router)

@app.get("/health")
def health():
    return {"status": "ok"}

