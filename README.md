# SSD-G29

## Flask app
Create an environment
```bat
py -3 -m venv .venv
```

Activate the environment
```bat
.venv\Scripts\activate
```

OPTIONAL: export all install package into requirements.txt
```bat
pip freeze > requirements.txt
```

Install Dependencies from requirements.txt
```bat
pip install -r requirements.txt
```

Run the Flask app
```bat
python app.py
```

<hr style="width:100%; height:1px; border:none; background-color:#ccc;">

## Docker
**Ensure Docker Desktop is running**

Build Docker Image
```bat
docker build -t safe-companions .
```

Create Container with a name. (RUN IT ONCE ONLY)
```bat
docker run -d -p 5000:5000 --name safe-companions-container safe-companions
```

Start/Stop the Container
```bat
docker start safe-companions-container
docker stop safe-companions-container
```