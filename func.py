from PIL import Image
import zipfile
import os
import uuid
import asyncio

async def cuImage(input_path, output_base_dir="output"):
    unique_folder = str(uuid.uuid4())[:8]
    output_dir = os.path.join(output_base_dir, unique_folder)
    
    output_width = 960
    output_height = 1280
    
    os.makedirs(output_dir, exist_ok=True)
    loop = asyncio.get_running_loop()

    def process_and_save_image():
        with Image.open(input_path) as img:
            if img.mode != 'RGB': 
                img = img.convert('RGB')
            resized_img = img.resize((output_width, output_height), Image.Resampling.LANCZOS)
            part_width = output_width // 3
            part_height = output_height // 3
            
            for row in range(3):
                for col in range(3):
                    left = col * part_width
                    upper = row * part_height
                    right = left + part_width
                    lower = upper + part_height
                    part = resized_img.crop((left, upper, right, lower))
                    filename = os.path.join(output_dir, f"part_{row+1}_{col+1}.jpg")
                    part.save(filename, "JPEG", quality=95)
        
        return output_dir
    
    output_folder = await loop.run_in_executor(None, process_and_save_image)
    return output_folder

async def zipArchive(output_path):
    zip_filename = f"{os.path.basename(output_path)}.zip"
    zip_path = os.path.join(os.path.dirname(output_path), zip_filename)
    loop = asyncio.get_running_loop()
    
    def create_zip():
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_path)
                    zipf.write(file_path, arcname)
        return zip_path
    
    zip_path = await loop.run_in_executor(None, create_zip)
    return zip_path