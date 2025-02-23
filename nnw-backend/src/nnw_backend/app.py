from fastapi import FastAPI
from models import init_db
from routers import auth, card

app = FastAPI()

init_db()
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(card.router)


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}


@app.get("/echo")
def echo(text: str = "Hello"):
    return {"echo": text}


def main():
    import uvicorn
    uvicorn.run("nnw_backend.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
