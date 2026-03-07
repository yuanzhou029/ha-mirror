import serial
import sys
import time
import argparse # 引入 argparse 模块用于命令行参数解析

# --- 默认串口参数设置 ---
# 这些值将作为 send_serial_data 函数的默认参数，
# 也可以通过命令行参数或直接在函数调用时覆盖。
DEFAULT_PORT = '/dev/ttyS1'    # 默认串口路径
DEFAULT_BAUDRATE = 9600        # 默认波特率
DEFAULT_BYTESIZE = serial.EIGHTBITS # 默认数据位 (8)
DEFAULT_PARITY = serial.PARITY_NONE # 默认校验位 (None)
DEFAULT_STOPBITS = serial.STOPBITS_ONE # 默认停止位 (1)
DEFAULT_TIMEOUT = 1            # 默认读取超时时间（秒）
DEFAULT_READ_RESPONSE = False  # 默认不读取响应

print(f"脚本启动，默认串口配置: PORT={DEFAULT_PORT}, BAUDRATE={DEFAULT_BAUDRATE}, ...")

def send_serial_data(
    data_to_send: str | bytes,
    port: str = DEFAULT_PORT,
    baudrate: int = DEFAULT_BAUDRATE,
    bytesize: int = DEFAULT_BYTESIZE,
    parity: str = DEFAULT_PARITY,
    stopbits: float = DEFAULT_STOPBITS,
    timeout: float = DEFAULT_TIMEOUT,
    read_response: bool = DEFAULT_READ_RESPONSE, # 新增参数：是否读取响应
    encoding: str = 'ascii' # 新增参数：数据编码方式
) -> tuple[bool, bytes | None]:
    """
    通过串口发送数据，并可选地读取响应。

    Args:
        data_to_send: 要发送的数据，可以是字符串或字节串。
        port: 串口设备路径，例如 '/dev/ttyUSB0' 或 '/dev/ttyS1'。
        baudrate: 波特率，例如 9600。
        bytesize: 数据位，例如 serial.EIGHTBITS (8)。
        parity: 校验位，例如 serial.PARITY_NONE ('N')。
        stopbits: 停止位，例如 serial.STOPBITS_ONE (1.0)。
        timeout: 读取超时时间（秒）。
        read_response: 如果为 True，将尝试从串口读取响应数据。
        encoding: 当 data_to_send 为字符串时，用于编码的字符集，默认为 'ascii'。

    Returns:
        tuple[bool, bytes | None]:
            第一个元素是布尔值，表示数据发送是否成功 (True/False)。
            第二个元素是字节串，如果 read_response 为 True 且收到数据，则为接收到的数据；否则为 None。
    """
    print(f"send_serial_data 函数被调用，准备发送: {data_to_send!r}")
    print(f"当前使用的串口参数: PORT={port}, BAUDRATE={baudrate}, BYTESIZE={bytesize}, PARITY={parity}, STOPBITS={stopbits}, TIMEOUT={timeout}, READ_RESPONSE={read_response}")
    
    received_data = None
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout
        )
        print(f"串口 {port} 已成功打开。")

        data_to_send_bytes: bytes
        if isinstance(data_to_send, str):
            try:
                data_to_send_bytes = data_to_send.encode(encoding)
                print(f"数据编码为 {encoding.upper()}: {data_to_send_bytes!r}")
            except UnicodeEncodeError as e:
                print(f"错误: 编码为 {encoding.upper()} 失败: {e}", file=sys.stderr)
                print(f"警告: 尝试使用 'utf-8' 编码: {data_to_send!r}")
                data_to_send_bytes = data_to_send.encode('utf-8')
        elif isinstance(data_to_send, bytes):
            data_to_send_bytes = data_to_send
            print(f"数据已经是字节串: {data_to_send_bytes!r}")
        else:
            print(f"警告: 传入数据类型非字符串或字节串 ({type(data_to_send)})，尝试转换为字符串并用 'ascii' 编码: {data_to_send!r}")
            data_to_send_bytes = str(data_to_send).encode('ascii')

        print(f"发送数据 (字节): {data_to_send_bytes!r}, 长度: {len(data_to_send_bytes)} 字节")
        ser.write(data_to_send_bytes)
        print("数据已写入串口.")
        time.sleep(0.1) # 给予设备响应时间，等待响应

        if read_response:
            # 尝试读取所有可用数据直到超时
            read_data = ser.read_all()
            if read_data:
                received_data = read_data
                print(f"收到响应: {received_data!r}")
                try:
                    print(f"响应 (尝试解码为 UTF-8): {received_data.decode('utf-8')!r}")
                except UnicodeDecodeError:
                    print("响应无法解码为 UTF-8。")
            else:
                print("未收到响应.")

        ser.close()
        print("串口已关闭.")
        return True, received_data

    except serial.SerialException as e:
        print(f"串口错误: {e}", file=sys.stderr)
        return False, None
    except Exception as e:
        print(f"发生未知错误: {e}", file=sys.stderr)
        return False, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="通过串口发送数据，支持自定义串口参数。")
    parser.add_argument("data", type=str, help="要发送的数据。如果是十六进制，请使用 --hex 选项。")
    parser.add_argument("--port", type=str, default=DEFAULT_PORT,
                        help=f"串口设备路径 (默认: {DEFAULT_PORT})。")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE,
                        help=f"波特率 (默认: {DEFAULT_BAUDRATE})。")
    parser.add_argument("--bytesize", type=int, default=DEFAULT_BYTESIZE,
                        choices=[serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS],
                        help=f"数据位 (5, 6, 7, 8) (默认: {DEFAULT_BYTESIZE})。")
    parser.add_argument("--parity", type=str, default=DEFAULT_PARITY,
                        choices=['N', 'E', 'O', 'M', 'S'],
                        help=f"校验位 (N=None, E=Even, O=Odd, M=Mark, S=Space) (默认: {DEFAULT_PARITY})。")
    parser.add_argument("--stopbits", type=float, default=DEFAULT_STOPBITS,
                        choices=[serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO],
                        help=f"停止位 (1.0, 1.5, 2.0) (默认: {DEFAULT_STOPBITS})。")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"读取超时时间（秒）(默认: {DEFAULT_TIMEOUT})。")
    parser.add_argument("--read-response", action="store_true", default=DEFAULT_READ_RESPONSE,
                        help=f"如果设置，脚本将尝试读取串口响应数据 (默认: {DEFAULT_READ_RESPONSE})。")
    parser.add_argument("--hex", action="store_true",
                        help="将要发送的数据视为十六进制字符串进行解析（例如 '010300000001840A'）。")
    parser.add_argument("--encoding", type=str, default='ascii',
                        help="当发送数据为字符串时使用的编码方式（例如 'ascii', 'utf-8', 'latin-1'） (默认: 'ascii')。")

    args = parser.parse_args()

    # 将命令行参数中的校验位字符串转换为 pyserial 常量
    parity_map = {
        'N': serial.PARITY_NONE,
        'E': serial.PARITY_EVEN,
        'O': serial.PARITY_ODD,
        'M': serial.PARITY_MARK,
        'S': serial.PARITY_SPACE,
    }
    
    data_to_send_processed = args.data
    if args.hex:
        try:
            # 移除数据中的空格（如果有），然后从十六进制字符串转换为字节串
            data_to_send_processed = bytes.fromhex(args.data.replace(" ", ""))
            print(f"已将十六进制字符串 '{args.data}' 解析为字节: {data_to_send_processed!r}")
        except ValueError as ve:
            print(f"错误: 无效的十六进制数据 '{args.data}' - {ve}", file=sys.stderr)
            sys.exit(1)

    success, response = send_serial_data(
        data_to_send=data_to_send_processed,
        port=args.port,
        baudrate=args.baudrate,
        bytesize=args.bytesize, # bytesize 默认值就是 pyserial 常量值 (5,6,7,8), 直接使用
        parity=parity_map.get(args.parity, DEFAULT_PARITY),
        stopbits=args.stopbits, # stopbits 默认值就是 pyserial 常量值 (1.0, 1.5, 2.0), 直接使用
        timeout=args.timeout,
        read_response=args.read_response,
        encoding=args.encoding
    )

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
