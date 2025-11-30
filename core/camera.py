# Class xử lý kết nối Camera
import cv2
from PIL import Image
import threading

class Camera:
    def __init__(self, source=0):
        """
        Khởi tạo Camera.
        :param source: 0 là webcam mặc định, hoặc đường dẫn file video.
        """
        self.source = source
        self.cap = None
        self.is_running = False

    def start(self):
        """Mở kết nối camera"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise ValueError("Không thể mở Camera. Vui lòng kiểm tra kết nối!")
            self.is_running = True

    def get_frame(self):
        """
        Đọc frame từ camera.
        
        Returns:
            image_pil: Đối tượng PIL Image để hiển thị lên UI (CustomTkinter).
            frame_rgb: Mảng Numpy (RGB) để đưa vào xử lý AI.
        """
        if self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # OpenCv dùng BGR, cần chuyển sang RGB cho PIL và AI Model
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Lật ảnh theo chiều ngang (flip) để tạo hiệu ứng gương
                frame_flip = cv2.flip(frame_rgb, 1)
                
                # Convert sang PIL Image
                image_pil = Image.fromarray(frame_flip)
                
                return image_pil, frame_flip
        return None, None

    def stop(self):
        """Giải phóng tài nguyên camera"""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None