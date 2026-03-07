#!/usr/bin/env python3
# send_tcp_command.py
import socket
import sys
import time

def hex_string_to_bytes(hex_str):
    """
    将一个空格分隔的十六进制字符串（例如：'01 0A FF'）转换为字节对象。
    """
    hex_str = hex_str.replace(" ", "").replace("0x", "").replace("x", "") # 移除空格和0x前缀
    if not hex_str:
        return b''
    
    # 检查是否为偶数长度，因为每个字节需要两个十六进制字符
    if len(hex_str) % 2 != 0:
        raise ValueError(f"无效的十六进制字符串长度 '{hex_str}'。十六进制字符数必须是偶数。")
        
    try:
        return bytes.fromhex(hex_str)
    except ValueError:
        raise ValueError(f"无效的十六进制字符 '{hex_str}'。请确保只包含有效的十六进制字符 (0-9, A-F)。")

def send_tcp_command(ip, port, command_input, append_cr_str, send_hex_str):
    # 将字符串参数转换为布尔值
    should_append_cr = append_cr_str.lower() == 'true'
    should_send_hex = send_hex_str.lower() == 'true'
    data_to_send = b'' # 初始化为字节对象
    
    # 定义一个变量来存储接收到的数值
    received_numeric_value = None 

    if should_send_hex:
        try:
            data_to_send = hex_string_to_bytes(command_input)
            print(f"命令字符串: '{command_input}'")
            print(f"解释为 HEX: -> {data_to_send.hex().upper()}")
        except ValueError as e:
            print(f"错误: {e}")
            sys.exit(1)
        
        if should_append_cr:
            # 如果是发送HEX且需要添加回车，则添加HEX的0D字节
            data_to_send += b'\x0D' 
            print(f"追加 HEX 回车符 (0D): {data_to_send.hex().upper()}")
    else:
        # 不是发送HEX，按普通字符串处理
        command_string = command_input
        if should_append_cr:
            command_string += '\r' # 追加ASCII回车符
        data_to_send = command_string.encode('utf-8') # 默认使用UTF-8编码
        print(f"命令字符串: '{command_input}'")
        print(f"解释为 ASCII/UTF-8: '{command_string.replace('\\r', '\\\\r')}'")

    print(f"连接到 {ip}:{port}")
    # 打印最终要发送的数据的HEX表示，便于调试
    print(f"最终发送数据 (HEX): {data_to_send.hex().upper()}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5) # 设置连接、发送和接收超时时间为5秒
            s.connect((ip, int(port)))
            s.sendall(data_to_send)
            print("数据已发送。")
            
            # ======== 接收响应部分 ========
            try:
                # 尝试接收最多 1024 字节的数据
                response = s.recv(1024) 
                if response:
                    print("\n--- 收到响应 ---")
                    decoded_response = None
                    try:
                        # 尝试将响应解码为 UTF-8 字符串，并去除首尾空白
                        decoded_response = response.decode('utf-8').strip()
                        print(f"收到响应 (文本): '{decoded_response}'")
                    except UnicodeDecodeError:
                        # 如果 UTF-8 解码失败，打印原始 HEX 数据
                        print(f"收到响应 (无法解码，HEX): {response.hex().upper()}")
                        
                    # ======== 处理接收到的数值 ========
                    if decoded_response:
                        # 尝试将解码后的字符串转换为整数或浮点数
                        try:
                            # 假设响应直接是数值，或者可以通过int/float转换
                            received_numeric_value = int(decoded_response)
                            print(f"提取到的数值 (整数): {received_numeric_value}")
                        except ValueError:
                            try:
                                received_numeric_value = float(decoded_response)
                                print(f"提取到的数值 (浮点数): {received_numeric_value}")
                            except ValueError:
                                print("响应中未检测到简单的数值（非整数或浮点数）。")
                    # ==================================
                else:
                    print("未收到响应。")
            except socket.timeout:
                print("接收响应超时（在5秒内未收到数据）。")
            # ==================================

            # ======== 等待关闭连接（如果需要） ========
            # 如果你确实需要在收到响应后仍然等待5秒再关闭连接，则保留此行。
            # 这对于某些需要连接保持一段时间的设备协议可能有用。
            # 如果你希望收到响应后立即关闭，可以移除这 5 秒的等待。
            #print("等待 5 秒后关闭连接...")
            #time.sleep(5) 
            # ==================================

    except socket.timeout:
        print("错误: Socket 操作超时（连接或发送）。")
    except ConnectionRefusedError:
        print("错误: 连接被拒绝。请检查 IP 地址和端口，或目标设备是否在线。")
    except Exception as e:
        print(f"发生意外错误: {e}")
    finally:
        print("连接已关闭。")
        # 可以在这里打印最终提取到的数值，例如：
        if received_numeric_value is not None:
            print(f"最终提取到的数值: {received_numeric_value}")

if __name__ == "__main__":
    if len(sys.argv) < 6: # 现在期望 5 个参数 + 脚本名 = 6
        print("用法: python send_tcp_command.py <ip> <port> <command> <append_cr> <send_hex>")
        sys.exit(1)
    
    ip_address = sys.argv[1]
    port_number = sys.argv[2]
    command_to_send = sys.argv[3]
    append_cr_param = sys.argv[4]
    send_hex_param = sys.argv[5] # 获取第五个参数

    send_tcp_command(ip_address, port_number, command_to_send, append_cr_param, send_hex_param)
