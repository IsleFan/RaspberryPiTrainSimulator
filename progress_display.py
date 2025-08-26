"""
進度顯示模組
負責即時顯示發送進度和狀態資訊
"""

import sys
import time
from datetime import datetime
from typing import Optional


class ProgressDisplay:
    def __init__(self):
        """
        初始化進度顯示器
        """
        self.start_time = None
        self.last_update_time = None
        self.total_sent = 0
        
    def start_display(self):
        """
        開始顯示，記錄開始時間
        """
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.total_sent = 0
        
        print("=" * 80)
        print("RS485 HEX資料傳送器 - 開始傳送")
        print("=" * 80)
        print("按 Ctrl+C 停止傳送")
        print()
    
    def update_progress(self, current_index: int, total_count: int, 
                       cycle_count: int, hex_string: str):
        """
        更新進度顯示
        
        Args:
            current_index: 當前資料索引 (1-based)
            total_count: 總資料筆數
            cycle_count: 循環次數
            hex_string: 當前傳送的HEX字串
        """
        current_time = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # 精確到毫秒
        
        # 計算進度百分比
        progress_percent = (current_index / total_count) * 100
        
        # 計算已運行時間
        elapsed_time = current_time - self.start_time if self.start_time else 0
        
        # 更新總發送數
        self.total_sent += 1
        
        # 計算發送速率（每秒）
        send_rate = self.total_sent / elapsed_time if elapsed_time > 0 else 0
        
        # 清除當前行並更新顯示
        print(f"\r時間: {timestamp} | "
              f"循環: {cycle_count} | "
              f"進度: {current_index}/{total_count} ({progress_percent:.1f}%) | "
              f"總發送: {self.total_sent} | "
              f"速率: {send_rate:.1f}/s", 
              end="", flush=True)
        
        # 每行顯示發送的HEX資料
        print(f"\n發送: {hex_string}")
        
        self.last_update_time = current_time
    
    def show_data_sent(self, hex_string: str, success: bool):
        """
        顯示資料發送狀態
        
        Args:
            hex_string: 發送的HEX字串
            success: 發送是否成功
        """
        status = "✓" if success else "✗"
        status_text = "成功" if success else "失敗"
        
        # 如果發送失敗，用紅色顯示（如果終端支援顏色）
        if not success:
            print(f"  狀態: {status} {status_text} - {hex_string}", 
                  file=sys.stderr, flush=True)
        
    def show_cycle_complete(self, cycle_count: int):
        """
        顯示循環完成訊息
        
        Args:
            cycle_count: 完成的循環次數
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 第 {cycle_count} 輪循環完成")
        print("-" * 60)
    
    def show_connection_status(self, is_connected: bool, port_info: dict):
        """
        顯示連接狀態
        
        Args:
            is_connected: 是否已連接
            port_info: 連接埠資訊
        """
        status_text = "已連接" if is_connected else "未連接"
        status_symbol = "✓" if is_connected else "✗"
        
        print(f"RS485狀態: {status_symbol} {status_text}")
        print(f"連接埠: {port_info.get('port', 'N/A')}")
        print(f"波特率: {port_info.get('baudrate', 'N/A')}")
        print()
    
    def show_file_info(self, filename: str, data_count: int):
        """
        顯示檔案載入資訊
        
        Args:
            filename: 檔案名稱
            data_count: 資料筆數
        """
        print(f"載入檔案: {filename}")
        print(f"資料筆數: {data_count}")
        print()
    
    def show_error(self, error_message: str):
        """
        顯示錯誤訊息
        
        Args:
            error_message: 錯誤訊息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 錯誤: {error_message}", file=sys.stderr, flush=True)
    
    def show_warning(self, warning_message: str):
        """
        顯示警告訊息
        
        Args:
            warning_message: 警告訊息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 警告: {warning_message}", flush=True)
    
    def show_summary(self):
        """
        顯示傳送摘要
        """
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            avg_rate = self.total_sent / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n")
            print("=" * 80)
            print("傳送摘要")
            print("=" * 80)
            print(f"總發送筆數: {self.total_sent}")
            print(f"運行時間: {elapsed_time:.2f} 秒")
            print(f"平均發送速率: {avg_rate:.2f} 筆/秒")
            print("=" * 80)
    
    def clear_line(self):
        """
        清除當前行
        """
        print("\r" + " " * 100 + "\r", end="", flush=True)
    
    def show_pause_status(self, is_paused: bool):
        """
        顯示暫停狀態
        
        Args:
            is_paused: 是否暫停中
        """
        if is_paused:
            print("\n[暫停中] 按任意鍵恢復傳送...")
        else:
            print("\n[恢復傳送]")
            
    @staticmethod
    def format_hex_string(hex_bytes: bytes) -> str:
        """
        格式化HEX字串顯示
        
        Args:
            hex_bytes: bytes資料
            
        Returns:
            str: 格式化的HEX字串
        """
        return ' '.join(f'{b:02X}' for b in hex_bytes)