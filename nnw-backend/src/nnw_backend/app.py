from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from models import init_db
from routers import auth, card, user_points_router, rewards_router

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Enable CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user_points_router.router,
                   prefix="/user", tags=["user_points"])
app.include_router(rewards_router.router, prefix="/rewards")

# Example endpoints
app.include_router(card.router)
app.include_router(user_points_router.router,
                   prefix="/user", tags=["user_points"])
app.include_router(rewards_router.router, prefix="/rewards")

# Example endpoints


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}


@app.get("/echo")
def echo(text: str = "Hello"):
    return {"echo": text}

# Main function to run the app


def main():
    import uvicorn
    uvicorn.run("nnw_backend.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
