# Complete Single Prompt to Recreate This Application

Copy the entire prompt below and give it to an AI assistant in one message. The assistant should produce the full application (backend + frontend + config + README) without needing follow-up prompts.

---

## PROMPT START (copy from here)

**Build a complete Employee Management Web Application as described below. Generate the entire codebase in one response: all backend and frontend files, config, and README. No placeholders—deliver runnable code.**

---

### 1. Tech stack

- **Backend:** Python 3.10+, Flask 3.x, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, psycopg2-binary, python-dotenv, Werkzeug (password hashing), email-validator. Use **PostgreSQL only** (no SQLite).
- **Frontend:** React 18+ with Vite, React Router, Axios, Recharts. Corporate blue/white theme.
- **Auth:** JWT (Bearer token in Authorization header). Two roles: `admin` and `employee`. Separate login pages and routes for admin vs employee.

---

### 2. Project structure

```
employee-management-app/
├── .gitignore          # Exclude .env, backend/venv/, frontend/node_modules/, *.db, backend/instance/
├── README.md            # Prerequisites, setup, run instructions, clone-and-run for others
├── backend/
│   ├── .env.example    # FLASK_APP, FLASK_ENV, SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD
│   ├── app.py          # create_app(), CORS (localhost:3000, 5173, 5174, 5175, 5176 + 127.0.0.1), register blueprints, db.create_all()
│   ├── config.py       # load_dotenv; DATABASE_URL required (PostgreSQL); reject YOUR_PASSWORD placeholder; Config class
│   ├── models.py       # SQLAlchemy: User, Department, Employee (see schema below)
│   ├── requirements.txt
│   ├── seed.py         # db.create_all(); create admin user from env; 5 departments; 10 sample employees with hierarchy; 1 employee user (john.smith / employee123)
│   ├── create_db.py    # Create PostgreSQL database employee_management if not exists (psycopg2)
│   ├── reset_admin.py  # Ensure admin user exists and set password from ADMIN_PASSWORD
│   └── routes/
│       ├── auth.py     # /register, /login/employee, /login/admin, /me (GET, JWT required)
│       ├── employees.py
│       ├── departments.py
│       └── reports.py
└── frontend/
    ├── package.json    # react, react-dom, react-router-dom, axios, recharts; vite, @vitejs/plugin-react
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx     # BrowserRouter, AuthProvider, routes below
        ├── api/axios.js # baseURL http://localhost:5000/api, withCredentials, Bearer token, 401/422 → clear storage and redirect to /
        ├── context/AuthContext.jsx  # user, loading, login(token, userData), logout; persist token/user in localStorage
        ├── index.css   # Global + corporate theme
        ├── components/
        │   ├── Layout.jsx   # Nav: Home, My Profile (employee), Employees/Departments/Org Tree/Reports (admin), Logout
        │   └── OrgTree.jsx  # Recursive tree from org-tree API
        └── pages/
            ├── Home.jsx           # Welcome; two cards: Employee (link /login/employee), Admin (link /login/admin); Register link; show session message if any
            ├── EmployeeLogin.jsx
            ├── EmployeeRegister.jsx
            ├── AdminLogin.jsx
            ├── EmployeeDashboard.jsx  # View/edit own profile (GET/PUT /employees/:id)
            ├── AdminDashboard.jsx     # Table of employees; search, filter by department & gender; sort by employee_id (default asc), first_name, last_name, email, job_title, department_id, date_joined; order asc/desc; Add/Edit/Delete employee modal
            ├── Departments.jsx        # List departments; Add/Edit/Delete
            ├── OrgTreePage.jsx         # Fetch /employees/org-tree, render OrgTree
            └── Reports.jsx             # Charts: department distribution, gender breakdown, joining trends, salary distribution; filter by department/gender; use Recharts
```

---

### 3. Database (PostgreSQL)

- **Table names must have capital first letter:** `Users`, `Departments`, `Employees` (so __tablename__ = 'Users' etc.).
- **Users:** id, email (unique), password_hash, role ('admin'|'employee'), created_at, employee_id (FK to Employees.id, nullable for admin).
- **Departments:** id, name (unique), description, created_at.
- **Employees:** id, employee_id (unique string e.g. EMP001), first_name, last_name, email (unique), phone, gender, date_of_birth, address, job_title, department_id (FK), manager_id (FK self), salary (Numeric), date_joined, created_at, updated_at. Relationships: department, manager (self), subordinates, user.
- **User:** set_password(password) and check_password(password) using Werkzeug pbkdf2:sha256.
- **Employee.to_dict()** must include department_name and manager_name (from relationships). **Employee.to_org_node()** for tree: id, employee_id, name, job_title, department, children (recursive).

---

### 4. Backend API (base path /api)

- **Auth** (prefix /api/auth):  
  - POST /register: body { email, password, first_name, last_name, phone?, job_title?, department_id?, manager_id? }. Create Employee + User (role employee). Return token + user + employee.  
  - POST /login/employee: body { email, password }. Return token, user, employee.  
  - POST /login/admin: body { email, password }. Return token, user.  
  - GET /me: JWT required. Return user (+ employee if role employee).
- **Employees** (prefix /api/employees, JWT required):  
  - GET: Admin gets all; employee gets only self. Query params: search, department_id, gender, **sort_by** (employee_id|first_name|last_name|email|job_title|department_id|date_joined), **order** (asc|desc). **Critical:** When sort_by=employee_id, sort by **numeric** value of the ID (e.g. EMP001→1, EMP002→2, EMP0011→11) so order is 1,2,3,...,11, not string sort. Use PostgreSQL regexp_replace to strip non-digits and cast to integer.  
  - GET /org-tree: Admin only. Return root employees with nested children (use to_org_node).  
  - GET /:id, POST, PUT /:id, DELETE /:id: Standard CRUD. Admin only for list/post/put/delete; employee can GET/PUT own.
- **Departments** (prefix /api/departments): GET, GET /:id, POST, PUT /:id, DELETE /:id. Admin only. Block delete if department has employees.
- **Reports** (prefix /api/reports): GET /dashboard. Admin only. Query params department_id, gender. Return: total_employees, by_department (name, count), by_gender (gender, count), joining_by_month (month, count), salary_distribution (buckets).

---

### 5. Frontend behavior

- **Routes:** / (Home), /login/employee, /login/admin, /register, /employee/dashboard (private), /admin/dashboard, /admin/departments, /admin/org-tree, /admin/reports (admin-only). PrivateRoute: redirect to / if no user; if adminOnly and role !== 'admin' redirect to /employee/dashboard.
- **Axios:** baseURL http://localhost:5000/api. Attach Authorization: Bearer &lt;token&gt; from localStorage. On 401 or 422, clear token/user, set sessionStorage message, redirect to /.
- **AuthContext:** On load, read user from localStorage (do not call /me by default). login(token, userData) saves token and user. logout clears storage.
- **AdminDashboard:** Fetch employees with params search, department_id, gender, sort_by, sortOrder. UI: dropdowns for Sort by (Employee ID, First name, Last name, Email, Job title, Department, Date joined) and Order (Ascending/Descending). Table: ID, Name, Email, Department, Job Title, Manager, Actions (Edit/Delete). Add Employee / Edit modal with form (first_name, last_name, email, phone, gender, date_of_birth, address, job_title, department_id, manager_id, salary, date_joined).
- **Reports:** Use Recharts (BarChart, LineChart, PieChart as needed). Fetch /reports/dashboard with filters.

---

### 6. Config and run

- **backend/.env.example:** DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@127.0.0.1:5432/employee_management, ADMIN_EMAIL=admin@company.com, ADMIN_PASSWORD=admin123, plus FLASK_APP, SECRET_KEY, JWT_SECRET_KEY.
- **README:** Prerequisites (Node 18+, Python 3.10+, PostgreSQL 12+). Steps: copy .env.example to .env and set DATABASE_URL; run create_db.py and seed.py; backend: venv, pip install -r requirements.txt, python app.py (port 5000); frontend: npm install, npm run dev. Default admin login admin@company.com / admin123. Mention that in PostgreSQL, when querying tables with capital names (Users, Departments, Employees), use double quotes: SELECT * FROM "Users";

---

### 7. Seed data

- Admin: one user (role admin) from ADMIN_EMAIL / ADMIN_PASSWORD.
- Departments: IT, HR, Finance, Marketing, Operations.
- Employees: 10 with hierarchy (e.g. CEO → VPs → Managers → Employees). One employee user: john.smith@company.com / employee123 linked to that employee.

---

### 8. Critical implementation details

- **JWT identity:** Use string identity: `create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'employee_id': user.employee_id})` for employee; admin only needs `role` in claims. In /me, parse identity as int for User.query.get(uid).
- **CORS:** Allow origins for localhost and 127.0.0.1 on ports 3000, 5173, 5174, 5175, 5176 so frontend works on any Vite port.
- **Employee list sort:** For sort_by=employee_id use PostgreSQL: `cast(coalesce(nullif(regexp_replace(employee_id, '[^0-9]', '', 'g'), ''), '0') as integer)` so EMP001, EMP002, EMP0011 sort as 1, 2, 11.
- **Registration:** Create Employee first, flush to get id, then create User with role='employee' and employee_id=emp.id. Return token with employee_id in claims.
- **Blueprint registration:** auth_bp at /api/auth, employees_bp at /api/employees, departments_bp at /api/departments, reports_bp at /api/reports.
- **config.py:** Raise ValueError at import if DATABASE_URL is missing or contains 'postgresql' or if it still contains 'YOUR_PASSWORD' or 'YOUR_POSTGRES_PASSWORD'.

---

**Deliver the full code for every file listed in the structure. Do not summarize or skip files. Output should be complete and runnable after cloning, creating .env, running create_db + seed, then starting backend and frontend.**

---

## PROMPT END (copy until here)
