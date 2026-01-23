import os
import logging
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
import aiofiles

# ------------------------------------------------------------
# 🔧 Logger
# ------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# 📁 Base directory: Images/
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2] / "Images"
BASE_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"[FileHandler] BASE_DIR = {BASE_DIR}")


# ------------------------------------------------------------
# 💾 Async File Save Function (Final Clean Version)
# ------------------------------------------------------------
async def save_picture(file: UploadFile, folder: str) -> str:
    """
    folder can be:
    - "Profile"
    - "ShopPic"
    - "CompanyPic"
    - "Medicine"
    - "MedicineType"
    - "MedicineCategory"
    - "Lab"
    - "Doctor"
    """

    if not file:
        raise ValueError("No file provided.")

    # --------------------------
    # Validate & sanitize folder
    # --------------------------
    folder = folder.strip("/\\")
    if ".." in folder or folder.startswith("."):
        raise ValueError("Invalid folder name")

    # Create subfolder
    upload_dir = BASE_DIR / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------
    # Prepare filename
    # --------------------------
    original_name = (file.filename or "file").replace(" ", "_")
    ext = original_name.split(".")[-1] if "." in original_name else ""
    filename = f"{uuid4()}.{ext}" if ext else str(uuid4())

    file_path = upload_dir / filename

    logger.info(f"[FileHandler] Saving: {original_name}")
    logger.info(f"[FileHandler] Target Path: {file_path}")

    # Reset stream pointer
    await file.seek(0)

    # --------------------------
    # Save file asynchronously
    # --------------------------
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(8192):
            await out.write(chunk)

    # --------------------------
    # Return path used for DB
    # --------------------------
    relative_path = file_path.relative_to(BASE_DIR.parent).as_posix()
    logger.info(f"[FileHandler] Saved Successfully: {relative_path}")

    return relative_path
