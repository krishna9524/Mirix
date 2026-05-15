import os
import shutil
import pypdf
import docx
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.memory_system.resource_memory import ResourceMemory 
from app.services.embedding_service import embedding_service
from app.services.vector_db_service import vector_db_service
from app.models.db_models import MemoryChunk 
import uuid
from fastapi.responses import FileResponse
from urllib.parse import unquote

# --- NEW IMPORTS FOR OCR & FILE TYPES ---
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
# --- END NEW IMPORTS ---


# Dependency getter
def get_resource_memory(db: Session = Depends(get_db)):
    return ResourceMemory(db)

router = APIRouter()
FILE_STORAGE_DIR = "mirix_file_storage"
os.makedirs(FILE_STORAGE_DIR, exist_ok=True)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
TEXT_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".py", ".js", ".css", ".html",
    ".cpp", ".c", ".h", ".java", ".json"
}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        client_filename = file.filename
        file_extension = os.path.splitext(client_filename)[1].lower()
        file_id = str(uuid.uuid4())
        new_filename = f"{file_id}{file_extension}"
        permanent_file_path = os.path.join(FILE_STORAGE_DIR, new_filename)
        file_content = ""
        embedding = None

        # Save the file permanently
        with open(permanent_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. --- Extract Text / Get Content (NOW WITH IMAGE OCR) ---
        if file_extension in IMAGE_EXTENSIONS:
            print(f"Processing image with OCR: {client_filename}")
            try:
                img = Image.open(permanent_file_path)
                file_content = pytesseract.image_to_string(img)
                if not file_content:
                    file_content = f"[No text found in image: {client_filename}]"
                print("Image OCR complete.")
            except Exception as e:
                print(f"Image OCR failed: {e}")
                file_content = f"[Error reading image file: {e}]"
            
            embedding = embedding_service.create_text_embedding(file_content)
        
        elif file_extension in TEXT_EXTENSIONS:
            print(f"Processing text file: {client_filename}")
            
            if file_extension == ".pdf":
                try:
                    reader = pypdf.PdfReader(permanent_file_path)
                    for page in reader.pages:
                        file_content += page.extract_text() or ""
                    file_content = file_content.strip()
                except Exception:
                    file_content = ""
                
                if not file_content:
                    print(f"PDF {client_filename} is empty or scanned. Starting OCR...")
                    try:
                        images = convert_from_path(permanent_file_path)
                        for img in images:
                            file_content += pytesseract.image_to_string(img) + "\n"
                        print("PDF OCR complete.")
                    except Exception as ocr_error:
                        print(f"PDF OCR process failed: {ocr_error}")
                        file_content = f"Error: Could not read scanned PDF. {ocr_error}"
            
            elif file_extension == ".docx":
                try:
                    doc = docx.Document(permanent_file_path)
                    for para in doc.paragraphs:
                        file_content += para.text + "\n"
                except Exception as e:
                    file_content = f"Error extracting text from docx: {client_filename}"
            
            else:
                try:
                    with open(permanent_file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except UnicodeDecodeError:
                    file_content = f"Error: File '{client_filename}' is not a valid text file."

            embedding = embedding_service.create_text_embedding(file_content)

        else:
            file_content = f"Unsupported file type: {client_filename}"
            embedding = embedding_service.create_text_embedding(file_content)
        
        # 2. --- Create MemoryChunk (SQL RAG) ---
        new_chunk = MemoryChunk(
            memory_type="resource",
            content=file_content
        )
        db.add(new_chunk)
        db.commit()
        db.refresh(new_chunk)
        sql_chunk_id = new_chunk.id

        # 3. --- Create Vector Embedding ---
        if embedding:
            if file_extension in IMAGE_EXTENSIONS:
                # We save image OCR text to the text index
                vector_db_service.add_text_embedding(embedding, sql_chunk_id)
            else:
                vector_db_service.add_text_embedding(embedding, sql_chunk_id)
        
        # 4. --- Save Metadata (Persistent SQL Store) ---
        resource_memory = ResourceMemory(db)
        resource_memory.add_file_metadata(
            file_id=file_id,
            filename=client_filename,
            path=permanent_file_path,
            chunk_id=sql_chunk_id
        )

        # 5. Save the FAISS indices to disk
        vector_db_service.save_indices()

        return {"file_id": file_id, "filename": client_filename, "sql_chunk_id": sql_chunk_id}

    except Exception as e:
        print(f"Error during file upload: {e}")
        if 'permanent_file_path' in locals() and os.path.exists(permanent_file_path):
            os.remove(permanent_file_path)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        await file.close()

@router.get("/get/{file_id}/{filename}")
async def get_stored_file(
    file_id: str,
    filename: str, # This param is just for user-friendly URLs
    db: Session = Depends(get_db)
):
    memory = ResourceMemory(db)
    metadata = memory.get_file_metadata(file_id) # This queries SQL

    if not metadata:
        print(f"File not found in DB for file_id: {file_id}")
        raise HTTPException(status_code=404, detail="File not found in memory.")
    
    stored_path = metadata.get('path')
    stored_filename = metadata.get('original_filename')

    if not os.path.exists(stored_path):
        print(f"File not found on disk at path: {stored_path}")
        raise HTTPException(status_code=404, detail="File not found on disk.")

    # --- THIS IS THE FIX ---
    # We change 'attachment' (force download) to 'inline' (try to open)
    return FileResponse(
        path=stored_path, 
        filename=stored_filename, 
        content_disposition_type="inline"
    )
    # --- END OF FIX ---