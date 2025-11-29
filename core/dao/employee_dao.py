from .base_dao import BaseDAO
from core.models.employee import Employee

class EmployeeDAO(BaseDAO):
    def select_all(self):
        self.cursor.execute("SELECT * FROM employees")
        rows = self.cursor.fetchall()
        return [Employee.from_row(row) for row in rows]

    def select_by_id(self, emp_id):
        self.cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        row = self.cursor.fetchone()
        return Employee.from_row(row)
    
    def select_by_username(self, username):
        self.cursor.execute("SELECT * FROM employees WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return Employee.from_row(row)

    def insert(self, emp: Employee):
        query = """
            INSERT INTO employees (username, password_hash, full_name, is_manager, status)
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (emp.username, emp.password_hash, emp.full_name, int(emp.is_manager), emp.status))
        self.commit()
        return self.cursor.lastrowid

    def update(self, emp: Employee):
        query = """
            UPDATE employees 
            SET username=?, password_hash=?, full_name=?, is_manager=?, status=?
            WHERE id=?
        """
        self.cursor.execute(query, (emp.username, emp.password_hash, emp.full_name, int(emp.is_manager), emp.status, emp.id))
        self.commit()

    def delete(self, emp_id):
        self.cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        self.commit()
        
    def soft_delete(self, emp_id):
        self.cursor.execute("UPDATE employees SET status='resigned' WHERE id = ?", (emp_id,))
        self.commit()