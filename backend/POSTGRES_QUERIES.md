# Querying the database (psql)

Tables are named with a capital first letter: **Users**, **Departments**, **Employees**.

In PostgreSQL, **use double quotes** when the name has capital letters:

```sql
SELECT * FROM "Users";
SELECT * FROM "Departments";
SELECT * FROM "Employees";
```

If you write `SELECT * FROM Users;` (no quotes), PostgreSQL looks for a table named `users` (lowercase) and gives: **relation "users" does not exist**.
