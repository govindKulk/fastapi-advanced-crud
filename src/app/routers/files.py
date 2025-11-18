
import os
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from app.models.database import User
from app.api import deps

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".doc", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Create upload directory if it do  esn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)



@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
) -> dict[str, str | int]:
    """ Upload File """

    if not file or not file.filename or file.filename == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds the maximum limit of {} bytes".format(MAX_FILE_SIZE))
    
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "message": "File uploaded successfully",
        "file_size": len(content)
    }

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(deps.get_current_active_user)
) -> FileResponse:
    """
    Download a file uploaded by the current user.
    Returns the actual file for download.
    """
    # Construct the file path with user ID prefix
    file_path = os.path.join(UPLOAD_DIR, f"{int(current_user.id)}_{filename}")  # type: ignore[arg-type]

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"File '{filename}' not found"
        )
    
    # Check if the file belongs to the current user (security check)
    if not os.path.basename(file_path).startswith(f"{int(current_user.id)}_"):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this file"
        )
    
    # Return the file as a downloadable response
    return FileResponse(
        path=file_path,
        filename=filename,  # Name to use when downloading
        media_type="application/octet-stream"  # Generic binary file type
    )

@router.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(deps.get_current_active_user)
) -> dict[str, str]:
    """
    Delete a file uploaded by the current user.
    """
    # Construct the file path with user ID prefix
    file_path = os.path.join(UPLOAD_DIR, f"{int(current_user.id)}_{filename}")  # type: ignore[arg-type]

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"File '{filename}' not found"
        )
    
    # Security check: ensure file belongs to current user
    if not os.path.basename(file_path).startswith(f"{int(current_user.id)}_"):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this file"
        )
    
    # Delete the file
    os.remove(file_path)
    
    return {
        "message": f"File '{filename}' deleted successfully"
    }

@router.get("/files")
async def list_user_files(
    current_user: User = Depends(deps.get_current_active_user),
) -> dict[str, list[str]]:
    """List all files uploaded by the current user"""
    user_files: list[str] = []
    if os.path.exists(UPLOAD_DIR):
        all_files = os.listdir(UPLOAD_DIR)
        user_files = [f for f in all_files if f.startswith(f"{current_user.id}_")]

    return {"files": user_files}
