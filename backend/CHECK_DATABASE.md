# How to Check Database Entries (PostgreSQL)

The app uses **PostgreSQL only**. Database name: `employee_management`.

---

## Quick check (Python script)

From the **backend** folder with venv activated:

```bat
python list_db.py
```

Prints all departments, employees, and users.

---

## Using psql

### 1. Connect

```bat
psql -U postgres -h 127.0.0.1 -p 5432 -d employee_management
```

Enter your PostgreSQL password when prompted.

### 2. Useful commands (inside psql)

```sql
\dt
```
List tables: `users`, `employees`, `departments`.

```sql
SELECT id, employee_id, first_name, last_name, email, job_title, department_id, manager_id FROM employees;
```

```sql
SELECT * FROM departments;
```

```sql
SELECT id, email, role, employee_id FROM users;
```

```sql
\q
```
Quit psql.

---

## One-shot from command line

```bat
set PGPASSWORD=your_password
psql -U postgres -h 127.0.0.1 -p 5432 -d employee_management -c "SELECT employee_id, first_name, last_name FROM employees;"
```

Replace `your_password` with your actual postgres password.
