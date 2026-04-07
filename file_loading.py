from fastapi import FastAPI, UploadFile, File
import numpy as np
import cv2

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in {'image/jpeg', 'image/png'}:
        return {"error": "Invalid file type. Only JPEG and PNG are allowed."}
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)               # Convert bytes to numpy array
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)           # Decode the image from the numpy array   
    if image is None:
        return {"error": "Could not decode the image. Please upload a valid image file."}
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return {"message": "File uploaded successfully", "image_shape": image.shape, "file_name": file.filename}