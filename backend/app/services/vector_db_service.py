import faiss
import numpy as np
import os
from app.services.embedding_service import embedding_service

# --- Text Index ---
TEXT_DIMENSION = 384 # From 'all-MiniLM-L6-v2'
TEXT_INDEX_FILE = "mirix_text_index.faiss"

# --- Image Index ---
IMAGE_DIMENSION = 512 # From 'clip-ViT-B-32'
IMAGE_INDEX_FILE = "mirix_image_index.faiss"

class VectorDBService:
    _instance = None
    _text_index = None
    _image_index = None

    def __new__(cls):
        if cls._instance is None:
            print("Initializing VectorDBService...")
            cls._instance = super(VectorDBService, cls).__new__(cls)
            
            # --- Text Index ---
            cls._text_index = faiss.IndexIDMap(faiss.IndexFlatL2(TEXT_DIMENSION))
            cls.load_text_index()
            
            # --- Image Index ---
            cls._image_index = faiss.IndexIDMap(faiss.IndexFlatL2(IMAGE_DIMENSION))
            cls.load_image_index()
            
            print("VectorDBService initialized (for text and images).")
        return cls._instance

    # --- Text Embedding Functions ---
    def add_text_embedding(self, embedding: list[float], chunk_id: int):
        try:
            vector = np.array([embedding]).astype('float32')
            chunk_id_np = np.array([chunk_id])
            self._text_index.add_with_ids(vector, chunk_id_np)
        except Exception as e:
            print(f"Error adding text embedding: {e}")

    def search_similar_text(self, query_text: str, k: int = 5) -> list[int]:
        query_vector = embedding_service.create_text_embedding(query_text)
        query_vector_np = np.array([query_vector]).astype('float32')
        try:
            D, I = self._text_index.search(query_vector_np, k)
            return [int(id) for id in I[0] if id != -1]
        except Exception as e:
            print(f"Error searching text index: {e}")
            return []

    # --- Image Embedding Functions ---
    def add_image_embedding(self, embedding: list[float], file_id: int):
        try:
            vector = np.array([embedding]).astype('float32')
            file_id_np = np.array([file_id])
            self._image_index.add_with_ids(vector, file_id_np)
        except Exception as e:
            print(f"Error adding image embedding: {e}")

    def search_similar_images(self, query_text: str, k: int = 3) -> list[int]:
        # We search the image index using the *text* query.
        # This is the magic of CLIP: text and images are in the same "space".
        query_vector = embedding_service.create_text_embedding(query_text)
        query_vector_np = np.array([query_vector]).astype('float32')
        try:
            D, I = self._image_index.search(query_vector_np, k)
            return [int(id) for id in I[0] if id != -1]
        except Exception as e:
            print(f"Error searching image index: {e}")
            return []

    # --- Index Save/Load Functions ---
    def save_indices(self):
        print("Saving FAISS indices...")
        try:
            faiss.write_index(self._text_index, TEXT_INDEX_FILE)
            faiss.write_index(self._image_index, IMAGE_INDEX_FILE)
            print("FAISS indices saved.")
        except Exception as e:
            print(f"Error saving indices: {e}")

    @staticmethod
    def load_text_index():
        if os.path.exists(TEXT_INDEX_FILE):
            try:
                cls = VectorDBService
                cls._text_index = faiss.read_index(TEXT_INDEX_FILE)
                print(f"Text index loaded. Total: {cls._text_index.ntotal}")
            except Exception as e: # <-- *** THIS IS THE FIX (removed comma) ***
                print(f"Error loading text index: {e}")
        else:
            print("No text index found. Starting new.")

    @staticmethod
    def load_image_index():
        if os.path.exists(IMAGE_INDEX_FILE):
            try:
                cls = VectorDBService
                cls._image_index = faiss.read_index(IMAGE_INDEX_FILE)
                print(f"Image index loaded. Total: {cls._image_index.ntotal}")
            except Exception as e:
                print(f"Error loading image index: {e}")
        else:
            print("No image index found. Starting new.")

vector_db_service = VectorDBService()