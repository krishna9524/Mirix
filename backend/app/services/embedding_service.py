from sentence_transformers import SentenceTransformer
from PIL import Image # <-- NEW: Import Pillow
import os

class EmbeddingService:
    _instance = None
    _text_model = None
    _image_model = None # <-- NEW: Image model

    def __new__(cls):
        if cls._instance is None:
            print("Initializing EmbeddingService (loading models)...")
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            
            # 1. Load Text Model
            cls._text_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 2. Load Image Model (CLIP)
            # SigLIP is a type of CLIP model. We'll use the standard one.
            cls._image_model = SentenceTransformer('clip-ViT-B-32')
            
            print("Embedding models (text & image) loaded.")
        return cls._instance

    def create_text_embedding(self, text: str) -> list[float]:
        """Converts text into a vector embedding."""
        if not text:
            return []
        embedding = self._text_model.encode(text).tolist()
        return embedding

    def create_image_embedding(self, image_path: str) -> list[float]:
        """Converts an image file into a vector embedding."""
        try:
            # Open the image file using Pillow
            img = Image.open(image_path)
            
            # The .encode() method for CLIP models can take an image object
            embedding = self._image_model.encode(img).tolist()
            return embedding
        except Exception as e:
            print(f"Error creating image embedding: {e}")
            return []

# --- The Singleton Instance ---
embedding_service = EmbeddingService()