#!/usr/bin/env python3
"""
RS485 HEX資料傳送器
主程式入口，提供CLI介面控制HEX資料透過RS485循環發送

使用方式:
    python main.py <hex_file>
    
範例:
    python main.py log_Sample.txt
"""

import sys
import argparse
import signal
import os
from hex_parser import HexParser
from rs485_comm import RS485Communicator
from sender_controller import SenderController
from progress_display import ProgressDisplay


class RS485HexSender:
    def __init__(self):
        """
        初始化RS485 HEX傳送器
        """
        self.rs485_comm = None
        self.sender_controller = None
        self.progress_display = ProgressDisplay()
        self.is_running = False
        
    def setup_signal_handlers(self):
        """
        設定訊號處理器，處理Ctrl+C中斷
        """
        def signal_handler(sig, frame):
            print("\n\n收到中斷訊號，正在停止傳送...")
            self.stop_sending()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def parse_arguments(self):
        """
        解析命令列參數
        
        Returns:
            argparse.Namespace: 解析後的參數
        """
        parser = argparse.ArgumentParser(
            description="RS485 HEX資料傳送器",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
範例:
    python main.py log_Sample.txt
    python main.py --port /dev/ttyUSB1 --baudrate 115200 data.txt
    python main.py --memory-efficient large_file.txt
    
支援的HEX檔案格式:
    每行包含以空格分隔的十六進制數值
    範例: 60 01 13 20 01 01 00 00 1C
    空白行分隔不同的數據塊
    
延遲規則:
    - "60 01 13 20" 開頭: 1000ms延遲
    - "60 01 13 30" 開頭: 10ms延遲
    - 其他: 10ms延遲
    
記憶體模式:
    --memory-efficient: 適合大型檔案，節省記憶體使用
            """
        )
        
        parser.add_argument(
            'hex_file', 
            help='包含HEX資料的檔案路徑'
        )
        
        parser.add_argument(
            '--port', '-p',
            default='/dev/ttyUSB0',
            help='RS485裝置路徑 (預設: /dev/ttyUSB0)'
        )
        
        parser.add_argument(
            '--baudrate', '-b',
            type=int,
            default=9600,
            help='波特率 (預設: 9600)'
        )
        
        parser.add_argument(
            '--single', '-s',
            action='store_true',
            help='只發送一輪，不循環'
        )
        
        parser.add_argument(
            '--test', '-t',
            action='store_true',
            help='測試模式，不實際發送資料'
        )
        
        parser.add_argument(
            '--memory-efficient', '-m',
            action='store_true',
            help='記憶體效率模式，適合處理大型檔案'
        )
        
        return parser.parse_args()
    
    def validate_hex_file(self, filename: str) -> bool:
        """
        驗證HEX檔案是否存在和可讀
        
        Args:
            filename: 檔案路徑
            
        Returns:
            bool: 檔案有效返回True
        """
        if not os.path.exists(filename):
            self.progress_display.show_error(f"檔案不存在: {filename}")
            return False
            
        if not os.path.isfile(filename):
            self.progress_display.show_error(f"路徑不是檔案: {filename}")
            return False
            
        if not os.access(filename, os.R_OK):
            self.progress_display.show_error(f"檔案無法讀取: {filename}")
            return False
            
        return True
    
    def initialize_rs485(self, port: str, baudrate: int, test_mode: bool = False) -> bool:
        """
        初始化RS485通訊
        
        Args:
            port: 串列埠路徑
            baudrate: 波特率
            test_mode: 測試模式
            
        Returns:
            bool: 初始化成功返回True
        """
        try:
            # 建立RS485通訊器配置
            rs485_config = {
                'port': port,
                'baudrate': baudrate,
                'timeout': 1,
                'write_timeout': 1
            }
            
            self.rs485_comm = RS485Communicator(rs485_config)
            
            if not test_mode:
                # 實際連接RS485裝置
                if not self.rs485_comm.connect():
                    self.progress_display.show_error("無法連接RS485裝置")
                    return False
            else:
                # 測試模式，模擬連接
                print("測試模式：跳過RS485實際連接")
                self.rs485_comm.is_connected = True
            
            # 顯示連接狀態
            port_info = self.rs485_comm.get_port_info()
            self.progress_display.show_connection_status(
                self.rs485_comm.is_connected, 
                port_info
            )
            
            return True
            
        except Exception as e:
            self.progress_display.show_error(f"初始化RS485失敗: {str(e)}")
            return False
    
    def setup_callbacks(self):
        """
        設定發送控制器的回調函數
        """
        # 進度更新回調
        self.sender_controller.set_progress_callback(
            self.progress_display.update_progress
        )
        
        # 資料發送回調
        self.sender_controller.set_data_sent_callback(
            self.progress_display.show_data_sent
        )
        
        # 循環完成回調
        self.sender_controller.set_cycle_complete_callback(
            self.progress_display.show_cycle_complete
        )
    
    def start_sending(self, hex_file: str, continuous: bool = True, memory_efficient: bool = False):
        """
        開始發送HEX資料
        
        Args:
            hex_file: HEX檔案路徑
            continuous: 是否循環發送
            memory_efficient: 是否使用記憶體效率模式
        """
        try:
            # 建立發送控制器
            self.sender_controller = SenderController(self.rs485_comm)
            
            # 載入HEX檔案
            if not self.sender_controller.load_hex_file(hex_file, memory_efficient):
                return False
            
            # 顯示檔案資訊
            status = self.sender_controller.get_status()
            data_count = status['total_data_count']
            mode_text = " (記憶體效率模式)" if memory_efficient else ""
            self.progress_display.show_file_info(hex_file, data_count)
            if memory_efficient:
                print(f"使用記憶體效率模式處理大型檔案{mode_text}")
            
            # 設定回調函數
            self.setup_callbacks()
            
            # 開始顯示
            self.progress_display.start_display()
            
            # 開始發送
            self.is_running = True
            self.sender_controller.start_sending(continuous)
            
            if continuous:
                # 循環模式，等待用戶中斷
                try:
                    while self.is_running and self.sender_controller.is_running:
                        import time
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
            else:
                # 單次模式，等待完成
                import time
                while self.sender_controller.is_running:
                    time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.progress_display.show_error(f"發送過程中發生錯誤: {str(e)}")
            return False
    
    def stop_sending(self):
        """
        停止發送
        """
        self.is_running = False
        
        if self.sender_controller:
            self.sender_controller.stop_sending()
            
        if self.rs485_comm and self.rs485_comm.is_connected:
            self.rs485_comm.disconnect()
            
        # 顯示摘要
        self.progress_display.show_summary()
    
    def run(self):
        """
        主執行函數
        """
        # 設定訊號處理器
        self.setup_signal_handlers()
        
        # 解析命令列參數
        args = self.parse_arguments()
        
        try:
            # 驗證HEX檔案
            if not self.validate_hex_file(args.hex_file):
                return 1
            
            # 初始化RS485
            if not self.initialize_rs485(args.port, args.baudrate, args.test):
                return 1
            
            # 開始發送
            continuous = not args.single
            success = self.start_sending(args.hex_file, continuous, args.memory_efficient)
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            print("\n用戶中斷")
            return 0
        except Exception as e:
            self.progress_display.show_error(f"程式執行錯誤: {str(e)}")
            return 1
        finally:
            self.stop_sending()


def main():
    """
    程式入口點
    """
    sender = RS485HexSender()
    exit_code = sender.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()