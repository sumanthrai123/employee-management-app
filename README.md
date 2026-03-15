# Employee Management Web Application

Corporate-style employee portal with **React** (frontend), **Flask** (backend), and **PostgreSQL** (database).

## Features

- **Employee Dashboard**: Register, sign in, view and update profile (Workday-style).
- **Admin Dashboard**: Full CRUD for employees, search by any field, filter by department and gender, sort by employee ID/name/etc., organization tree, and departments management.
- **Reports Dashboard**: Charts for department distribution, gender breakdown, joining trends, and salary distribution; filters by department and gender.
- **Authentication**: Separate login pages for Employee and Admin; JWT-based auth with roles.

## Tech Stack

- **Frontend**: React (Vite), React Router, Axios, Recharts
- **Backend**: Python Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- **Database**: PostgreSQL

---

## Requirements (what users need to run the app)

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Node.js** | 18+ (LTS recommended) | Run frontend (npm, Vite) |
| **Python** | 3.10+ | Run backend (Flask) |
| **PostgreSQL** | 12+ | Database (required; no SQLite) |
| **Git** | Any | Clone the repo |

### Backend dependencies (Python)

Installed via `pip install -r backend/requirements.txt`:

| Package | Version |
|---------|---------|
| Flask | 3.0.0 |
| Flask-SQLAlchemy | 3.1.1 |
| Flask-CORS | 4.0.0 |
| Flask-JWT-Extended | 4.6.0 |
| psycopg2-binary | ≥2.9.5 |
| python-dotenv | 1.0.0 |
| Werkzeug | 3.0.1 |
| email-validator | 2.1.0 |

### Frontend dependencies (Node)

Installed via `npm install` in `frontend/`:

- **react**, **react-dom** (^19.x)
- **react-router-dom** (^7.x)
- **axios** (^1.x)
- **recharts** (^3.x)
- **vite** (^8.x), **@vitejs/plugin-react**, **eslint**, etc. (dev)

---

## Prerequisites (summary)

- **Node.js** 18+
- **Python** 3.10+
- **PostgreSQL** 12+ (installed and running; you need the `postgres` user password)

---

## Upload project to GitHub

1. **Create a new repository on GitHub**  
   Go to [github.com](https://github.com) → **New repository**. Name it (e.g. `employee-management-app`). Do **not** add a README, .gitignore, or license (we already have them).

2. **Initialize Git and push** (run from the project root `employee-management-app/`):

   ```bash
   git init
   git add .
   git commit -m "Initial commit: Employee Management App"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name (e.g. `sumanthrai123` / `employee-management-app`).

3. **Important:** The `.gitignore` already excludes `.env`, `venv`, and `node_modules`, so secrets and heavy folders are not uploaded. Anyone who clones the repo must create their own `backend/.env` (see below).

---

## Setup (for anyone who cloned / downloaded the repo)

### 1. Create `backend/.env` (required)

The repo does **not** include `.env` (secrets). Copy the example and edit:

- **Windows:** `cd backend` then `copy .env.example .env`
- **macOS/Linux:** `cd backend` then `cp .env.example .env`

Edit `.env` and set **DATABASE_URL** = `postgresql://postgres:YOUR_POSTGRES_PASSWORD@127.0.0.1:5432/employee_management` (replace `YOUR_POSTGRES_PASSWORD` with your PostgreSQL password). Optionally set **ADMIN_EMAIL** and **ADMIN_PASSWORD** (defaults: admin@company.com / admin123).

### 2. PostgreSQL database (required – no SQLite)

The app uses **PostgreSQL only**. Ensure PostgreSQL is installed and running.

**Windows (easiest):** From `backend` folder, run `run_postgres_setup.bat` and enter your Postgres password. This creates the `employee_management` database, tables, and default admin + sample data.

**Or manually:** From `backend`, run `python create_db.py` then `python seed.py`.

Default admin: **admin@company.com** / **admin123** (change in production.)

### 3. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows CMD
# or: venv\Scripts\Activate.ps1   # Windows PowerShell (run Set-ExecutionPolicy RemoteSigned -Scope CurrentUser if needed)
source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

Then run the API:

```bash
python app.py
```

API runs at **http://localhost:5000**.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at **http://localhost:5173** (Vite default).

## Usage

1. **Home** (`/`): Choose Employee or Admin sign-in.
2. **Employee**: Register (`/register`) or sign in (`/login/employee`), then use **My Profile** to view/edit your details.
3. **Admin**: Sign in (`/login/admin`). Then:
   - **Employees**: List, search, filter by department/gender, Add/Edit/Delete.
   - **Departments**: Create and manage departments.
   - **Org Tree**: View reporting hierarchy (CEO → VP → Manager → Employee).
   - **Reports**: View charts (department, gender, joining trends, salary) and filter by department/gender.

## Project Structure

```
employee-management-app/
├── backend/
│   ├── app.py           # Flask app and blueprints
│   ├── config.py        # Config and env
│   ├── models.py        # User, Employee, Department
│   ├── seed.py          # DB create + default admin + sample departments
│   ├── requirements.txt
│   └── routes/
│       ├── auth.py     # Register, login employee/admin, /me
│       ├── employees.py # CRUD, search, org-tree
│       ├── departments.py
│       └── reports.py   # Dashboard stats and chart data
└── frontend/
    └── src/
        ├── api/axios.js
        ├── context/AuthContext.jsx
        ├── components/ Layout, OrgTree
        ├── pages/       Home, *Login, *Dashboard, Reports, Departments, OrgTreePage
        ├── App.jsx
        └── index.css    # Corporate blue/white theme
```

## Design

- Corporate blue/white theme (Workday-style).
- Responsive layout; modals for Add/Edit forms; tables for lists; Recharts for reports.
