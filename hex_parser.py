"""
HEX檔案解析模組
用於解析包含HEX字串的檔案，並轉換為可發送的資料格式
"""

import re
from typing import List, Tuple


class HexParser:
    def __init__(self, filename: str):
        self.filename = filename
        self.hex_data = []
        
    def parse_file(self) -> List[Tuple[bytes, int]]:
        """
        解析HEX檔案並返回 (資料bytes, 延遲毫秒) 的列表
        
        Returns:
            List[Tuple[bytes, int]]: [(hex_bytes, delay_ms), ...]
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            self.hex_data = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # 跳過空行
                if not line:
                    continue
                    
                # 解析HEX字串
                hex_bytes = self._parse_hex_line(line)
                if hex_bytes:
                    # 判斷延遲時間
                    delay_ms = self._get_delay_time(hex_bytes)
                    self.hex_data.append((hex_bytes, delay_ms))
                    
            return self.hex_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到檔案: {self.filename}")
        except Exception as e:
            raise Exception(f"解析檔案時發生錯誤: {str(e)}")
    
    def _parse_hex_line(self, line: str) -> bytes:
        """
        將HEX字串行轉換為bytes
        
        Args:
            line: HEX字串行，如 "60 01 13 20 01 01 00 00 1C"
            
        Returns:
            bytes: 轉換後的bytes資料
        """
        # 移除所有非十六進制字符，保留0-9, A-F, a-f
        hex_string = re.sub(r'[^0-9A-Fa-f]', '', line)
        
        # 確保字串長度為偶數
        if len(hex_string) % 2 != 0:
            return None
            
        try:
            # 每兩個字符轉換為一個byte
            hex_bytes = bytes.fromhex(hex_string)
            return hex_bytes
        except ValueError:
            return None
    
    def _get_delay_time(self, hex_bytes: bytes) -> int:
        """
        根據HEX資料的開頭判斷延遲時間
        
        Args:
            hex_bytes: HEX資料bytes
            
        Returns:
            int: 延遲毫秒數
        """
        if len(hex_bytes) < 4:
            return 10  # 預設延遲
            
        # 檢查前四個bytes
        header = hex_bytes[:4]
        
        if header == b'\x60\x01\x13\x20':  # "60 01 13 20"
            return 90
        elif header == b'\x60\x01\x13\x30':  # "60 01 13 30"
            return 10
        else:
            return 10  # 預設延遲
    
    def get_hex_string(self, hex_bytes: bytes) -> str:
        """
        將bytes轉換為可讀的HEX字串格式
        
        Args:
            hex_bytes: bytes資料
            
        Returns:
            str: 格式化的HEX字串，如 "60 01 13 20 01 01"
        """
        return ' '.join(f'{b:02X}' for b in hex_bytes)
    
    def get_total_count(self) -> int:
        """
        獲取總資料筆數
        
        Returns:
            int: 資料筆數
        """
        return len(self.hex_data)