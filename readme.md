# Init commands

## Set up the enviroment
.\venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Run project locally
uvicorn main:app --reload

## Run the project in a Host IP and Port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload