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
                # 生成隨機顏色
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
        """使用指定模型進行預測"""
        try:
            # 確保模型已加載
            if model_type not in self.models:
                print(f"Model {model_type.value} not loaded, loading now...")
                load_result = self.load_model(model_type)
                if not load_result["success"]:
                    raise Exception(f"Failed to load model: {load_result['error']}")

            model = self.models[model_type]
            print(f"Using model: {model_type.value}")
            
            if model_type == ModelType.CELLPOSE:
                print("Starting Cellpose prediction...")
                print(f"Input image shape: {image.shape}")
                
                masks, flows, styles = model.eval(
                    image, 
                    channels=[2, 1],
                    min_size=0,
                    do_3D=False
                )
                
                print(f"Prediction completed. Mask shape: {masks.shape}")
                
                # 創建 mask 預覽
                mask_preview = self.create_mask_preview(masks)
                
                result = {
                    "model_name": "Cellpose",
                    "num_cells": len(np.unique(masks)) - 1,
                    "processing_time": "N/A",
                    "mask_preview": mask_preview  # 添加 mask 預覽
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