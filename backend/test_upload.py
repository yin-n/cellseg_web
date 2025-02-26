import numpy as np
import requests

# 創建測試數據
test_array = np.random.rand(100, 100)

# 保存為 .npy 文件
np.save('test_array.npy', test_array)

# 上傳文件
with open('test_array.npy', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': ('test_array.npy', f, 'application/octet-stream')}
    )

print(response.json())
