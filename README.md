# RS485 HEX Data Sender

一個專為 Raspberry Pi 設計的 RS485 HEX 資料傳送器，可透過 USB 轉 RS485 介面循環發送十六進制資料。

## 功能特色

- 🔄 **智能循環發送**: 自動循環發送 HEX 資料檔案中的所有內容
- ⏱️ **智能延遲控制**: 根據資料開頭自動調整延遲時間
  - `60 01 13 20` 開頭: 90ms 延遲
  - `60 01 13 30` 開頭: 10ms 延遲
  - 其他: 10ms 延遲
- 📊 **即時進度顯示**: 顯示傳送進度、循環次數、發送速率
- 🔌 **RS485 支援**: 支援 USB 轉 RS485 通訊介面
- 🎛️ **靈活配置**: 可自訂串列埠、波特率等參數
- 🧪 **測試模式**: 無需實際硬體即可測試程式邏輯

## 系統需求

- **硬體**: Raspberry Pi 4
- **作業系統**: Raspberry Pi OS (64-bit)
- **Python**: Python 3.6+
- **硬體介面**: USB 轉 RS485 轉換器

## 安裝

1. 複製專案
```bash
git clone https://github.com/yourusername/RaspberryPiTrainSimulator.git
cd RaspberryPiTrainSimulator
```

2. 安裝依賴套件
```bash
pip install -r requirements.txt
```

3. 確保程式可執行
```bash
chmod +x main.py
```

## 使用方式

### 基本使用

```bash
python main.py log_Sample.txt
```

### 進階參數

```bash
# 自訂串列埠和波特率
python main.py --port /dev/ttyUSB1 --baudrate 115200 data.txt

# 單次發送（不循環）
python main.py --single log_Sample.txt

# 測試模式（無需實際硬體）
python main.py --test log_Sample.txt

# 顯示幫助
python main.py --help
```

## HEX 資料檔案格式

支援的 HEX 檔案格式範例：

```
60 01 13 20 01 01 00 00 1C 00 00 00 00 00 00 11
05 14 03 65 90 00 00 18 FD 12 F0 00 00 00 00 00
10 52 05 30 54 05 00 00 02 00 00 00 01 FE E3

60 01 13 30 01 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 68 0F 63 04 00 FF 00 00 00
```

- 每行包含以空格分隔的十六進制數值
- 空行會被自動忽略
- 支援大小寫十六進制字符

## 程式架構

```
RaspberryPiTrainSimulator/
├── main.py              # 主程式入口，CLI 介面
├── hex_parser.py        # HEX 字串檔案解析器
├── rs485_comm.py        # RS485 通訊模組
├── sender_controller.py # 發送控制器（循環邏輯）
├── progress_display.py  # 進度顯示模組
├── requirements.txt     # Python 套件需求
├── log_Sample.txt       # 範例資料檔案
└── README.md           # 說明文件
```

## 預設 RS485 參數

| 參數 | 預設值 |
|------|--------|
| 連接埠 | `/dev/ttyUSB0` |
| 波特率 | `9600` |
| 資料位 | `8` |
| 校驗位 | `無` |
| 停止位 | `1` |
| 超時 | `1秒` |

## 使用範例

### 循環發送模式
```bash
$ python main.py log_Sample.txt

================================================================================
RS485 HEX資料傳送器 - 開始傳送
================================================================================
按 Ctrl+C 停止傳送

RS485狀態: ✓ 已連接
連接埠: /dev/ttyUSB0
波特率: 9600

載入檔案: log_Sample.txt
資料筆數: 22

時間: 14:15:25.313 | 循環: 1 | 進度: 22/22 (100.0%) | 總發送: 22 | 速率: 53.1/s
發送: 00 00 00 00 01 B4 E9

[14:15:25] 第 1 輪循環完成
------------------------------------------------------------
```

### 單次發送模式
```bash
$ python main.py --single log_Sample.txt
# 發送完一輪後自動停止
```

### 測試模式
```bash
$ python main.py --test log_Sample.txt
# 不需要實際 RS485 硬體，用於測試程式邏輯
```

## 錯誤排除

### 常見問題

1. **找不到 RS485 裝置**
   ```bash
   # 檢查 USB 裝置
   lsusb
   
   # 檢查串列埠
   ls /dev/ttyUSB*
   ```

2. **權限不足**
   ```bash
   # 將用戶加入 dialout 群組
   sudo usermod -a -G dialout $USER
   
   # 重新登入生效
   ```

3. **模組不存在錯誤**
   ```bash
   # 安裝 pyserial
   pip install pyserial
   ```

## 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 作者

由 Claude Code 協助開發

---

**注意**: 使用前請確保正確連接 RS485 硬體，並設定適當的電氣參數以避免設備損壞。