#!/usr/bin/env python3
# send_tcp_command.py
import socket
import sys
import time

def send_tcp_command(ip, port, command):
    """
    向指定的IP和端口发送TCP命令。
    """
    try:
        # 创建一个TCP/IP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 连接到服务器
        server_address = (ip, int(port))
        print(f"DEBUG: Attempting to connect to {server_address[0]} port {server_address[1]}...", file=sys.stderr) # 增加日志
        sock.settimeout(5) # 设置连接和发送/接收超时为5秒
        sock.connect(server_address)
        print(f"DEBUG: Successfully connected to {server_address[0]} port {server_address[1]}.", file=sys.stderr) # 增加日志
        try:
            # 编码并发送数据
            # *** 关键修改：在命令末尾添加回车符 \r ***
            # 许多设备要求命令以回车符或换行符结束
            message = (command + "\r").encode('ascii') 
            print(f"DEBUG: Sending '{command}\\r' ({len(message)} bytes) to {ip}:{port}...", file=sys.stderr) # 增加日志，显示添加了\r
            sock.sendall(message)
            print(f"DEBUG: Command sent successfully.", file=sys.stderr) # 增加日志
            
            # （可选）接收服务器响应，如果你的调试助手会返回数据
            # 除非你的设备有需要读取的响应，否则通常不需要这部分
            # sock.settimeout(1) # 可以设置一个短的读取超时
            # try:
            #     data = sock.recv(1024)
            #     if data:
            #         print(f"DEBUG: Received response: '{data.decode('ascii').strip()}'", file=sys.stderr)
            # except socket.timeout:
            #     print(f"DEBUG: No response received from {ip}:{port} within timeout.", file=sys.stderr)
            # except Exception as e_recv:
            #     print(f"DEBUG: Error receiving response from {ip}:{port}: {e_recv}", file=sys.stderr)
                
        finally:
            print(f"DEBUG: Closing socket for {ip}:{port}.", file=sys.stderr) # 增加日志
            sock.close()
    except socket.timeout as e:
        print(f"ERROR: Connection or send/receive timed out for {ip}:{port} with command '{command}': {e}", file=sys.stderr)
        sys.exit(1) # 表示脚本执行失败
    except ConnectionRefusedError as e:
        print(f"ERROR: Connection refused by {ip}:{port}. Is the device on and listening? {e}", file=sys.stderr)
        sys.exit(1) # 表示脚本执行失败
    except Exception as e:
        # 错误信息会记录到 Home Assistant 的日志中
        print(f"ERROR: An unexpected error occurred while sending TCP command to {ip}:{port} with command '{command}': {e}", file=sys.stderr)
        sys.exit(1) # 表示脚本执行失败

if __name__ == "__main__":
    # 脚本需要接收3个参数：IP地址、端口号、命令字符串
    if len(sys.argv) != 4:
        print("Usage: python send_tcp_command.py <IP_ADDRESS> <PORT> <COMMAND_STRING>", file=sys.stderr)
        sys.exit(1)
    
    ip_address = sys.argv[1]
    port_number = sys.argv[2]
    command_string = sys.argv[3]
    
    send_tcp_command(ip_address, port_number, command_string)
