import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
from numpy.linalg import norm

class FeatureExtractor:
    def __init__(self):
        """
        Khởi tạo mô hình MobileNetV2 đã được huấn luyện trên ImageNet.
        include_top=False: Bỏ lớp phân loại cuối cùng, chỉ lấy lớp đặc trưng.
        pooling='avg': Lấy trung bình để ra vector 1 chiều.
        """
        self.model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        print("MobileNetV2 loaded successfully.")

    def extract(self, img):
        """
        Trích xuất đặc trưng từ ảnh.
        Input: PIL Image hoặc Numpy Array (RGB)
        Output: Vector đặc trưng 1 chiều (numpy array)
        """
        # Đảm bảo đầu vào là PIL Image để resize đúng chuẩn
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
            
        # Resize về 224x224
        img = img.resize((224, 224))
        
        # Chuyển sang mảng numpy và thêm chiều batch
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        
        # Tiền xử lý theo chuẩn MobileNetV2 (đưa pixel về khoảng -1 đến 1)
        x = preprocess_input(x)
        
        # Dự đoán (trích xuất đặc trưng)
        feature = self.model.predict(x, verbose=0) # verbose=0 để tắt log rác
        
        # Flatten để trả về vector 1 chiều
        return feature.flatten()

class VectorSearch:
    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Tính độ tương đồng Cosine giữa 2 vector.
        Công thức: (A . B) / (||A|| * ||B||)
        Kết quả từ -1 đến 1. Càng gần 1 càng giống nhau.
        """
        return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    @staticmethod
    def search(query_vector, db_vectors, top_k=5):
        """
        Tìm kiếm các vector giống nhất trong database.
        
        Input: 
            - query_vector: Vector đặc trưng của ảnh cần tìm.
            - db_vectors: List các tuple (product_id, vector_numpy) lấy từ DB.
            - top_k: Số lượng kết quả muốn trả về.
            
        Output: 
            - List các product_id có độ tương đồng cao nhất.
        """
        scores = []
        
        for pid, vec in db_vectors:
            if vec is None: 
                continue
            
            # Tính độ tương đồng
            score = VectorSearch.cosine_similarity(query_vector, vec)
            
            # Chỉ lấy kết quả có độ tương đồng > 0.5 (Ngưỡng tự chọn)
            if score > 0.4: 
                scores.append((score, pid))
        
        # Sắp xếp giảm dần theo điểm số (độ tương đồng)
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Lấy top K kết quả và lọc trùng lặp product_id 
        # (Vì 1 sản phẩm có thể có nhiều ảnh, ta chỉ cần lấy ID sản phẩm 1 lần)
        results = []
        seen_ids = set()
        
        for score, pid in scores:
            if pid not in seen_ids:
                results.append(pid)
                seen_ids.add(pid)
                if len(results) >= top_k:
                    break
                    
        return results