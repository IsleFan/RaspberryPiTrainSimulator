"""
RS485通訊模組
用於透過USB轉RS485介面發送資料到串列埠
"""

import serial
import time
from typing import Optional


class RS485Communicator:
    # 預設RS485參數設定
    DEFAULT_CONFIG = {
        'port': '/dev/ttyUSB0',     # USB轉RS485預設裝置路徑
        'baudrate': 9600,           # 波特率
        'bytesize': serial.EIGHTBITS,  # 資料位數
        'parity': serial.PARITY_NONE,   # 校驗位
        'stopbits': serial.STOPBITS_ONE,  # 停止位
        'timeout': 1,               # 讀取超時(秒)
        'write_timeout': 1          # 寫入超時(秒)
    }
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化RS485通訊器
        
        Args:
            config: RS485設定參數字典，如果為None則使用預設值
        """
        self.config = {**self.DEFAULT_CONFIG}
        if config:
            self.config.update(config)
            
        self.serial_port = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """
        連接RS485裝置
        
        Returns:
            bool: 連接成功返回True，失敗返回False
        """
        try:
            self.serial_port = serial.Serial(
                port=self.config['port'],
                baudrate=self.config['baudrate'],
                bytesize=self.config['bytesize'],
                parity=self.config['parity'],
                stopbits=self.config['stopbits'],
                timeout=self.config['timeout'],
                write_timeout=self.config['write_timeout']
            )
            
            # 等待連接穩定
            time.sleep(0.1)
            
            self.is_connected = True
            return True
            
        except serial.SerialException as e:
            print(f"RS485連接失敗: {str(e)}")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"連接時發生未預期錯誤: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """
        中斷RS485連接
        """
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.is_connected = False
            except Exception as e:
                print(f"中斷連接時發生錯誤: {str(e)}")
    
    def send_data(self, data: bytes) -> bool:
        """
        發送資料到RS485
        
        Args:
            data: 要發送的bytes資料
            
        Returns:
            bool: 發送成功返回True，失敗返回False
        """
        if not self.is_connected:
            return False
            
        # 測試模式：沒有實際serial_port但is_connected為True
        if not self.serial_port:
            return True
            
        try:
            # 清除緩衝區
            if self.serial_port.in_waiting:
                self.serial_port.reset_input_buffer()
            if self.serial_port.out_waiting:
                self.serial_port.reset_output_buffer()
            
            # 發送資料
            bytes_written = self.serial_port.write(data)
            
            # 確保資料被發送出去
            self.serial_port.flush()
            
            return bytes_written == len(data)
            
        except serial.SerialTimeoutException:
            print("發送資料時超時")
            return False
        except serial.SerialException as e:
            print(f"發送資料時發生串列埠錯誤: {str(e)}")
            return False
        except Exception as e:
            print(f"發送資料時發生未預期錯誤: {str(e)}")
            return False
    
    def get_port_info(self) -> dict:
        """
        獲取目前RS485連接資訊
        
        Returns:
            dict: 連接資訊字典
        """
        return {
            'port': self.config['port'],
            'baudrate': self.config['baudrate'],
            'is_connected': self.is_connected,
            'is_open': self.serial_port.is_open if self.serial_port else False
        }
    
    def __enter__(self):
        """
        支援with語句的內容管理器
        """
        if self.connect():
            return self
        else:
            raise Exception("無法連接到RS485裝置")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with語句結束時自動中斷連接
        """
        self.disconnect()