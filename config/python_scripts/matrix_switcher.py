# /config/python_scripts/matrix_switcher.py
hass = hass
logger.info("DEBUG_CONFIRM: matrix_switcher.py v2.2-FINAL-FORMAT script started and loaded.")

# **** 重要：input_select 实体ID定义 ****
input_select_source_id = 'input_select.matrix_source_selector'      # 输入源选择器的实体ID
input_select_destination_id = 'input_select.matrix_destination_selector' # 输出设备选择器的实体ID

# **** 重要：input_name_to_port_map 的键与 input_select.matrix_source_selector 的 options 完全一致 ****
# 这里的 "1", "3" 等是矩阵切换器接收的“输入指令码”
input_name_to_port_map = {
    "PS5": "1",          # 假设 PS5 对应输入指令码 1
    "PC": "3",           # 假设 PC 对应输入指令码 3
    "Switch": "2",       # 假设 Switch 对应输入指令码 2
    "机顶盒": "4",       # 假设 机顶盒 对应输入指令码 4
    "HDMI1": "0",        # 假设 HDMI1 对应输入指令码 0
    "HDMI2": "5"         # 假设 HDMI2 对应输入指令码 5
}

# **** 重要：output_name_to_port_map 的键与 input_select.matrix_destination_selector 的 options 完全一致 ****
# 这里的 "0", "1" 等是矩阵切换器接收的“输出指令码”
output_name_to_port_map = {
    "TV": "0",          # 假设 TV 对应输出指令码 0
    "Monitor": "1",     # 假设 Monitor 对应输出指令码 1
    "Projector": "2"    # 假设 Projector 对应输出指令码 2
}

should_proceed = True
selected_input_friendly_name = None
source_port_string = None
selected_output_friendly_name = None
output_port_string = None

# 1. 获取选定的输入源
selected_input_state = hass.states.get(input_select_source_id)
if not selected_input_state:
    logger.error(f"无法获取 {input_select_source_id} 的状态，脚本停止。")
    should_proceed = False

if should_proceed:
    selected_input_friendly_name = selected_input_state.state
    logger.debug(f"DEBUG: 从 '{input_select_source_id}' 获取到的选择输入友好名称: '{selected_input_friendly_name}'")

    source_port_string = input_name_to_port_map.get(selected_input_friendly_name)
    logger.debug(f"DEBUG: 根据友好名称 '{selected_input_friendly_name}' 查找到的输入指令码: '{source_port_string}'")

    if source_port_string is None:
        logger.error(f"未知的输入源名称: '{selected_input_friendly_name}'，或未在 input_name_to_port_map 中定义。脚本停止。")
        should_proceed = False

# 2. 获取选定的输出设备
if should_proceed:
    selected_output_state = hass.states.get(input_select_destination_id)
    if not selected_output_state:
        logger.error(f"无法获取 {input_select_destination_id} 的状态，脚本停止。")
        should_proceed = False

if should_proceed:
    selected_output_friendly_name = selected_output_state.state
    logger.debug(f"DEBUG: 从 '{input_select_destination_id}' 获取到的选择输出友好名称: '{selected_output_friendly_name}'")

    output_port_string = output_name_to_port_map.get(selected_output_friendly_name)
    logger.debug(f"DEBUG: 根据友好名称 '{selected_output_friendly_name}' 查找到的输出指令码: '{output_port_string}'")

    if output_port_string is None:
        logger.error(f"未知的输出设备名称: '{selected_output_friendly_name}'，或未在 output_name_to_port_map 中定义。脚本停止。")
        should_proceed = False

# 3. 构建矩阵命令字符串 (格式为 {输出指令码}{输入指令码})
matrix_command = "" # 初始化为空字符串

if should_proceed: # 只有当输入和输出都成功确定后才构建命令
    matrix_command = f"{output_port_string}{source_port_string}"
    logger.info(f"将要发送的最终矩阵命令: '{matrix_command}'")

# 4. 调用 shell_command 服务发送命令
if should_proceed:
    hass.services.call(
        'shell_command',
        'send_cmd',
        {
            'ip': '192.168.3.116',
            'port': '4001', # 确保这是字符串类型，而不是数字
            'command': matrix_command
        },
        blocking=True
    )
    logger.info(f"已发送矩阵命令: '{matrix_command}' 到 192.168.3.116:4001")
