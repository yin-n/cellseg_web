import torch
import numpy as np
from typing import Dict, Any
from enum import Enum
from pathlib import Path
from cellpose import models
import cv2
import base64

class ModelType(Enum):
    CELLPOSE = "cellpose"
    # 可以添加其他模型類型

class BrainModel:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.current_model = None
        print(f"Using device: {self.device}")

    def load_model(self, model_type: ModelType):
        """加載指定類型的模型"""
        try:
            if model_type not in self.models:
                print(f"Loading {model_type.value}...")
                
                if model_type == ModelType.CELLPOSE:
                    # 更新模型路徑
                    weights_file = "/mnt/aperto/yin/napari_cellseg/napari_cellseg3d/code_models/models/pretrained/cellpose_split1.6780841"
                    if not Path(weights_file).exists():
                        raise FileNotFoundError(f"Model weights not found at {weights_file}")
                    
                    self.models[model_type] = models.CellposeModel(
                        device=self.device,
                        pretrained_model=weights_file
                    )
                    print("Cellpose model loaded successfully")
            
            self.current_model = model_type
            return {"success": True, "message": f"Loaded {model_type.value}"}
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return {"success": False, "error": str(e)}

    def create_mask_preview(self, masks: np.ndarray) -> str:
        """將 mask 轉換為彩色圖像並返回 base64 編碼"""
        try:
            # 創建彩色標籤圖像
            mask_rgb = np.zeros((masks.shape[0], masks.shape[1], 3), dtype=np.uint8)
            
            # 為每個細胞分配不同的顏色
            unique_labels = np.unique(masks)[1:]  # 跳過背景（0）
            for label in unique_labels:
                # 生成隨機顏色，但保持一致性
                np.random.seed(int(label))  # 確保同一個標籤總是得到相同的顏色
                color = np.random.randint(0, 255, 3)
                mask_rgb[masks == label] = color
            
            # 轉換為 PNG 格式的 base64 字符串
            _, buffer = cv2.imencode('.png', mask_rgb)
            mask_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return f"data:image/png;base64,{mask_base64}"
        except Exception as e:
            print(f"Error creating mask preview: {e}")
            raise

    def predict(self, image: np.ndarray, model_type: ModelType) -> Dict[str, Any]:
        """使用指定模型進行預測，對於4D數據只處理中間部分"""
        is_3d = len(image.shape) == 4  # (C, D, H, W)   
        try:
            if model_type == ModelType.CELLPOSE:
                print("Starting Cellpose prediction...")
                print(f"Input image shape: {image.shape}")
                
                # 確保模型已加載
                if model_type not in self.models:
                    print(f"Loading model {model_type.value}...")
                    load_result = self.load_model(model_type)
                    if not load_result["success"]:
                        raise Exception(f"Failed to load model: {load_result.get('error', 'Unknown error')}")
                
                # 處理4D數據
                if len(image.shape) == 4:  # (C, D, H, W)
                    print("Processing 4D data...")
                    image = image[:, 20:60, 128:384, 128:384] 
                    print(f"Selected middle channels, new shape: {image.shape}")
                    
                    # 確保數據格式正確 (2, D, H, W)
                    if image.shape[0] != 2:
                        raise ValueError(f"Expected 2 channels for prediction, got {image.shape[0]}")
                
                # 使用已加載的模型進行預測
                masks, flows, styles = self.models[model_type].eval(
                    image, 
                    channels=[2, 1],
                    min_size=0,
                    do_3D=is_3d  # 因為我們處理的是3D數據
                )
                
                print(f"Prediction completed. Mask shape: {masks.shape}")
                
                # 生成預覽
                if len(masks.shape) == 3:  # 3D mask
                    mask_previews = []
                    for z in range(masks.shape[0]):
                        preview = self.create_mask_preview(masks[z])
                        mask_previews.append({
                            'depth': z,
                            'preview': preview
                        })
                    
                    result = {
                        "model_name": "Cellpose",
                        "num_cells": len(np.unique(masks)) - 1,
                        "processing_time": "N/A",
                        "mask_previews": mask_previews,
                        "is_3d": True
                    }
                else:
                    # 2D mask 處理（保持原有邏輯）
                    mask_preview = self.create_mask_preview(masks)
                    result = {
                        "model_name": "Cellpose",
                        "num_cells": len(np.unique(masks)) - 1,
                        "processing_time": "N/A",
                        "mask_preview": mask_preview,
                        "is_3d": False
                    }
                
                return result
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            raise

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """預處理輸入圖像"""
        try:
            # 確保輸入是正確的形狀 (2, 256, 256)
            if image.shape != (2, 256, 256):
                raise ValueError(f"Expected shape (2, 256, 256), got {image.shape}")
            
            return image
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            raise 