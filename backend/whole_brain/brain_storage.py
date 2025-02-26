import zarr
import s3fs
import numpy as np
from typing import Optional, Dict, Any

class BrainStorage:
    def __init__(self):
        # 初始化 S3 文件系統
        self.s3 = s3fs.S3FileSystem(
            key='YOUR_AWS_ACCESS_KEY',
            secret='YOUR_AWS_SECRET_KEY',
            client_kwargs={'region_name': 'YOUR_REGION'}
        )
        
        self.bucket = 'your-brain-data-bucket'
        
    def save_brain_data(self, 
                       data_path: str,
                       s3_path: str,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        將本地 zarr 數據上傳到 S3
        
        :param data_path: 本地 zarr 文件路徑
        :param s3_path: S3 中的目標路徑
        :param metadata: 額外的元數據
        """
        try:
            # 打開本地 zarr
            local_zarr = zarr.open(data_path, mode='r')
            
            # 創建 S3 存儲
            store = s3fs.S3Map(root=f"{self.bucket}/{s3_path}", s3=self.s3)
            
            # 創建新的 zarr 組
            remote_zarr = zarr.group(store=store, overwrite=True)
            
            # 複製數據
            for name, array in local_zarr.arrays():
                # 使用與原始數組相同的壓縮設置
                compressor = array.compressor
                chunks = array.chunks
                
                # 創建目標數組
                remote_zarr.create_dataset(
                    name,
                    shape=array.shape,
                    chunks=chunks,
                    dtype=array.dtype,
                    compressor=compressor
                )
                
                # 分塊複製數據以節省內存
                for i in range(0, array.shape[0], chunks[0]):
                    end = min(i + chunks[0], array.shape[0])
                    remote_zarr[name][i:end] = array[i:end]
            
            # 保存元數據
            if metadata:
                remote_zarr.attrs.put(metadata)
            
            return f"{self.bucket}/{s3_path}"
            
        except Exception as e:
            print(f"Error saving brain data: {e}")
            raise

    def load_brain_data(self, s3_path: str) -> zarr.Group:
        """
        從 S3 加載 zarr 數據
        
        :param s3_path: S3 中的數據路徑
        :return: zarr 組
        """
        try:
            store = s3fs.S3Map(root=f"{self.bucket}/{s3_path}", s3=self.s3)
            return zarr.group(store=store)
            
        except Exception as e:
            print(f"Error loading brain data: {e}")
            raise

    def get_chunk(self, 
                 s3_path: str, 
                 array_name: str, 
                 slice_info: tuple) -> np.ndarray:
        """
        只獲取特定的數據切片
        
        :param s3_path: S3 中的數據路徑
        :param array_name: 要訪問的數組名稱
        :param slice_info: 切片信息，例如 (0, 100, 0, 100, 0, 100)
        :return: numpy 數組
        """
        try:
            zarr_group = self.load_brain_data(s3_path)
            array = zarr_group[array_name]
            
            # 將切片信息轉換為適當的切片對象
            slices = tuple(slice(start, end) for start, end in zip(slice_info[::2], slice_info[1::2]))
            return array[slices]
            
        except Exception as e:
            print(f"Error getting chunk: {e}")
            raise