# NagarDrishti

AI-ready civic complaint reporting platform.

## Features
- Citizen registration/login
- Civic problem reporting
- Photo upload
- GPS latitude/longitude
- Automatic Tracking ID
- Acknowledgement slip
- Complaint tracking
- Separate Department Login
- Department dashboard
- Status updates
- SQLite database
- Flask REST API

## Run backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend: http://localhost:5000

## Run frontend

Open the `frontend` folder with VS Code Live Server.

Default API URL is:
http://localhost:5000/api

For deployment, set `API_URL` in browser localStorage to your Render API URL, for example:
```js
localStorage.setItem("API_URL", "https://YOUR-RENDER-SERVICE.onrender.com/api")
```

## Department login (development default)

Email:
department@nagardrishti.gov.in

Password:
Department@123

For production, set `DEPARTMENT_EMAIL` and `DEPARTMENT_PASSWORD_HASH` as Render environment variables. Do not commit real credentials.

## GitHub

Upload the whole `NagarDrishti` folder to your GitHub repository. Keep `database.db` out of GitHub for production if you use a hosted persistent database.
