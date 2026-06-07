# EcoScan ATM

EcoScan ATM is a Plastic Bottle ATM web application built with Python, HTML, and CSS. It provides an interface to scan plastic bottles, track recycling activity, and manage related data.

## Frontend Preview

![EcoScan ATM Frontend](./frontend-preview.png)

> Note: Place your screenshot image file as `frontend-preview.png` in the root of the repository.  
> If you keep it inside a folder like `assets/`, update the path above to `./assets/frontend-preview.png`.

---

## Project Structure

- `templates/` — HTML templates for the frontend views.
- `static/css/` — CSS files for styling the user interface.
- `app.py` — Main application entry point (web server / routes).
- `bottle_scanner.py` — Logic related to bottle scanning.
- `models.py` — Data models / database-related code.
- `init_db.py` — Script to initialize or set up the database.
- `requirements.txt` — Python dependencies for this project.

---

## How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/Shivaprasad008/-EcoScan-ATM.git
cd -EcoScan-ATM
```

### 2. Create and activate a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python init_db.py
```

### 5. Run the application

```bash
python app.py
```

Then open your browser and go to:

```text
http://localhost:5000
```

to view the EcoScan ATM frontend.
