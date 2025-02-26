from brain_storage import BrainStorage
import zarr
import numpy as np

def main():
    storage = BrainStorage()
    
    # 示例：保存數據
    # 假設我們有一個本地的 zarr 文件
    local_path = "path/to/your/brain.zarr"
    s3_path = "brain_data/subject_001"
    
    metadata = {
        'subject_id': 'sub-001',
        'acquisition_date': '2024-01-20',
        'modality': 'calcium_imaging',
        'resolution': (0.5, 0.5, 1.0),
        'units': 'um'
    }
    
    # 上傳到 S3
    s3_url = storage.save_brain_data(local_path, s3_path, metadata)
    print(f"Data saved to: {s3_url}")
    
    # 加載整個數據集
    brain_data = storage.load_brain_data(s3_path)
    print("Available arrays:", list(brain_data.array_keys()))
    print("Metadata:", dict(brain_data.attrs))
    
    # 只加載特定區域
    chunk = storage.get_chunk(
        s3_path,
        'calcium_data',  # 假設這是數組名稱
        (0, 100, 0, 100, 0, 100)  # 獲取 100x100x100 的立方體
    )
    print("Chunk shape:", chunk.shape)

if __name__ == "__main__":
    main()
