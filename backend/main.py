from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import numpy as np
import io
import cv2
import tifffile
import os
import base64
# 這裡導入您的模型
# from your_model import YourModel
import uvicorn
from model_handler import BrainModel, ModelType
import traceback

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模型處理器
model_handler = BrainModel()

def load_file_to_numpy(contents: bytes, filename: str) -> np.ndarray:
    """
    根據文件類型將內容轉換為 numpy array
    """
    try:
        file_ext = os.path.splitext(filename)[1].lower()
        print(f"Processing file with extension: {file_ext}")
        
        if file_ext in ['.npy']:
            # 處理 numpy 文件
            return np.load(io.BytesIO(contents))
            
        elif file_ext in ['.tif', '.tiff']:
            # 處理 TIFF 文件
            return tifffile.imread(io.BytesIO(contents))
            
        else:
            # 處理其他圖片格式
            nparr = np.frombuffer(contents, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
    except Exception as e:
        print(f"Error in load_file_to_numpy: {str(e)}")
        print(traceback.format_exc())
        raise

def create_channel_preview(channel_array: np.ndarray) -> str:
    """將單個通道轉換為 base64 編碼的 PNG 圖片"""
    try:
        # 標準化到 0-255 範圍
        if channel_array.dtype != np.uint8:
            normalized = ((channel_array - channel_array.min()) / 
                        (channel_array.max() - channel_array.min()) * 255).astype(np.uint8)
        else:
            normalized = channel_array

        # 轉換為 PNG
        _, buffer = cv2.imencode('.png', normalized)
        img_str = base64.b64encode(buffer).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        raise ValueError(f"無法創建預覽: {str(e)}")

@app.post("/api/preview")
async def get_preview(file: UploadFile = File(...)):
    """生成多通道預覽"""
    try:
        print(f"Receiving file: {file.filename}")  # 調試信息
        contents = await file.read()
        img_array = load_file_to_numpy(contents, file.filename)
        
        print(f"Loaded array shape: {img_array.shape}, dtype: {img_array.dtype}")  # 調試信息
        
        # 確保數組是 3D 的 (channels, height, width)
        if len(img_array.shape) != 3:
            print(f"Unexpected shape: {img_array.shape}")  # 調試信息
            raise ValueError(f"預期輸入為 3D 數組 (channels, height, width)，但得到 {img_array.shape}")
        
        # 為每個通道創建預覽
        previews = []
        for i in range(img_array.shape[0]):
            print(f"Processing channel {i}")  # 調試信息
            preview_data = create_channel_preview(img_array[i])
            previews.append({
                'channel': i,
                'preview': preview_data
            })
        
        response_data = {
            "success": True,
            "previews": previews,
            "shape": img_array.shape,
            "dtype": str(img_array.dtype),
            "num_channels": img_array.shape[0]
        }
        print(f"Sending response with {len(previews)} previews")  # 調試信息
        return response_data
        
    except Exception as e:
        print(f"Error in preview generation: {str(e)}")  # 調試信息
        return {"success": False, "error": str(e)}

@app.get("/api/models")
async def get_available_models():
    """獲取可用的模型列表"""
    return {
        "models": [
            {"id": model.value, "name": model.name} 
            for model in ModelType
        ]
    }

@app.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...),
    model_type: str = "cellpose"  # 默認使用 cellpose
):
    try:
        print(f"Receiving file: {file.filename}")
        contents = await file.read()
        print("File read successfully")

        print("Loading file into numpy array...")
        img_array = load_file_to_numpy(contents, file.filename)
        print(f"Array loaded with shape: {img_array.shape}, dtype: {img_array.dtype}")
        
        print(f"Using model type: {model_type}")
        model_enum = ModelType(model_type)
        
        print("Starting prediction...")
        prediction_result = model_handler.predict(img_array, model_enum)
        print("Prediction completed")
        
        return {
            "success": True,
            "imageId": "temp_id",
            "shape": img_array.shape,
            "dtype": str(img_array.dtype),
            "filename": file.filename,
            "prediction": prediction_result
        }
    except Exception as e:
        print("Error in upload_image:")
        print(traceback.format_exc())  # 打印完整的錯誤堆棧
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 