"""
發送控制器模組
負責管理循環發送邏輯和時間控制
"""

import time
import threading
from typing import List, Tuple, Callable
from hex_parser import HexParser
from rs485_comm import RS485Communicator


class SenderController:
    def __init__(self, rs485_comm: RS485Communicator):
        """
        初始化發送控制器
        
        Args:
            rs485_comm: RS485通訊器實例
        """
        self.rs485_comm = rs485_comm
        self.hex_data = []
        self.current_index = 0
        self.cycle_count = 0
        self.is_running = False
        self.is_paused = False
        self.total_sent = 0
        
        # 回調函數
        self.on_progress_callback = None
        self.on_data_sent_callback = None
        self.on_cycle_complete_callback = None
        
    def load_hex_file(self, filename: str) -> bool:
        """
        載入HEX檔案
        
        Args:
            filename: HEX檔案路徑
            
        Returns:
            bool: 載入成功返回True，失敗返回False
        """
        try:
            parser = HexParser(filename)
            self.hex_data = parser.parse_file()
            self.current_index = 0
            self.cycle_count = 0
            self.total_sent = 0
            
            if not self.hex_data:
                print("警告: 檔案中沒有有效的HEX資料")
                return False
                
            print(f"成功載入 {len(self.hex_data)} 筆HEX資料")
            return True
            
        except Exception as e:
            print(f"載入HEX檔案失敗: {str(e)}")
            return False
    
    def set_progress_callback(self, callback: Callable):
        """
        設定進度更新回調函數
        
        Args:
            callback: 回調函數，接收 (current_index, total_count, cycle_count, hex_string)
        """
        self.on_progress_callback = callback
    
    def set_data_sent_callback(self, callback: Callable):
        """
        設定資料發送回調函數
        
        Args:
            callback: 回調函數，接收 (hex_string, success)
        """
        self.on_data_sent_callback = callback
    
    def set_cycle_complete_callback(self, callback: Callable):
        """
        設定循環完成回調函數
        
        Args:
            callback: 回調函數，接收 (cycle_count)
        """
        self.on_cycle_complete_callback = callback
    
    def start_sending(self, continuous: bool = True):
        """
        開始發送資料
        
        Args:
            continuous: True為循環發送，False為發送一次
        """
        if not self.hex_data:
            print("錯誤: 沒有載入HEX資料")
            return
            
        if not self.rs485_comm.is_connected:
            print("錯誤: RS485未連接")
            return
            
        self.is_running = True
        self.is_paused = False
        
        if continuous:
            # 在新執行緒中執行循環發送
            self.send_thread = threading.Thread(target=self._continuous_send_loop)
            self.send_thread.daemon = True
            self.send_thread.start()
        else:
            # 發送一輪
            self._send_one_cycle()
            self.is_running = False
    
    def stop_sending(self):
        """
        停止發送
        """
        self.is_running = False
        self.is_paused = False
    
    def pause_sending(self):
        """
        暫停發送
        """
        self.is_paused = True
    
    def resume_sending(self):
        """
        恢復發送
        """
        self.is_paused = False
    
    def _continuous_send_loop(self):
        """
        循環發送主迴圈
        """
        while self.is_running:
            if not self.is_paused:
                self._send_one_cycle()
                
                # 循環完成回調
                if self.on_cycle_complete_callback:
                    self.on_cycle_complete_callback(self.cycle_count)
            else:
                # 暫停時短暫休眠
                time.sleep(0.1)
    
    def _send_one_cycle(self):
        """
        發送一個完整循環的資料
        """
        if not self.hex_data:
            return
            
        self.cycle_count += 1
        
        for i, (hex_bytes, delay_ms) in enumerate(self.hex_data):
            if not self.is_running or self.is_paused:
                break
                
            self.current_index = i + 1
            
            # 轉換為可讀字串格式
            hex_string = ' '.join(f'{b:02X}' for b in hex_bytes)
            
            # 進度回調
            if self.on_progress_callback:
                self.on_progress_callback(
                    self.current_index, 
                    len(self.hex_data), 
                    self.cycle_count, 
                    hex_string
                )
            
            # 發送資料
            success = self.rs485_comm.send_data(hex_bytes)
            
            if success:
                self.total_sent += 1
            
            # 資料發送回調
            if self.on_data_sent_callback:
                self.on_data_sent_callback(hex_string, success)
            
            # 根據資料類型延遲
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)  # 轉換為秒
        
        # 重置索引為下一輪準備
        self.current_index = 0
    
    def get_status(self) -> dict:
        """
        獲取目前發送狀態
        
        Returns:
            dict: 狀態資訊字典
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_index': self.current_index,
            'total_data_count': len(self.hex_data),
            'cycle_count': self.cycle_count,
            'total_sent': self.total_sent
        }
    
    def get_current_hex_string(self) -> str:
        """
        獲取目前發送的HEX字串
        
        Returns:
            str: 目前的HEX字串
        """
        if 0 <= self.current_index - 1 < len(self.hex_data):
            hex_bytes, _ = self.hex_data[self.current_index - 1]
            return ' '.join(f'{b:02X}' for b in hex_bytes)
        return ""