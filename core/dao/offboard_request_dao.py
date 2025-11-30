from .base_dao import BaseDAO
from core.models.offboard_request import OffboardRequest

class OffboardRequestDAO(BaseDAO):
    def insert(self, req: OffboardRequest):
        query = "INSERT INTO offboard_requests (employee_id, reason, status) VALUES (?, ?, ?)"
        self.cursor.execute(query, (req.employee_id, req.reason, req.status))
        self.commit()
        return self.cursor.lastrowid

    def select_all_pending(self):
        # Join với bảng employees để lấy tên nhân viên
        query = """
            SELECT r.*, e.full_name 
            FROM offboard_requests r
            JOIN employees e ON r.employee_id = e.id
            WHERE r.status = 'pending'
            ORDER BY r.request_date DESC
        """
        self.cursor.execute(query)
        return [OffboardRequest.from_row(row) for row in self.cursor.fetchall()]

    def update_status(self, req_id, status):
        query = "UPDATE offboard_requests SET status = ? WHERE id = ?"
        self.cursor.execute(query, (status, req_id))
        self.commit()

    def get_by_employee_id(self, emp_id):
        query = "SELECT * FROM offboard_requests WHERE employee_id = ? ORDER BY request_date DESC"
        self.cursor.execute(query, (emp_id,))
        return [OffboardRequest.from_row(row) for row in self.cursor.fetchall()]