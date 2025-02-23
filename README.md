# NNW Backend Setup Instructions

## Prerequisites
- Python 3.9+
- pipx installed ([pipx installation guide](https://pypa.github.io/pipx/installation/))

## Setup Steps

1. **Unzip the project archive**
```bash
unzip nnw-backend.zip
```

2. **Navigate to the project root**
```bash
cd backend
```

3. **Install Poetry using pipx**
```bash
pipx install poetry
```

4. **Install project dependencies**
```bash
cd nnw-backend && poetry install
```

5. **Start the FastAPI server**
```bash
cd src && poetry run start
```

## Accessing the Server
The FastAPI server should now be running at:
```
http://localhost:8000
```

If you encounter any issues, please contact the Team 31 for support.

