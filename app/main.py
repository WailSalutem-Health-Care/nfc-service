from fastapi import FastAPI
from app.messaging.consumer import NfcEventConsumer
from app.nfc.router import router as nfc_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
consumer = NfcEventConsumer()

app.include_router(nfc_router)

@app.on_event("startup")
def start_consumer():
    consumer.start()

@app.on_event("shutdown")
def stop_consumer():
    consumer.stop()

@app.get("/health")
def health():
    return {"status": "ok"}

