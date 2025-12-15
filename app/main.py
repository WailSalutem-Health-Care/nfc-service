from fastapi import FastAPI

app = FastAPI(title="NFC Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "nfc-service"}