import math
import numpy as np # 用于统计计算，需要安装 pip install numpy
import sympy # 用于符号计算和求导，需要安装 pip install sympy
from decimal import Decimal, getcontext, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_HALF_DOWN # 导入 decimal 模块及舍入模式

# --- 常量和辅助函数 ---
# t因子，这里只是一个默认值，实际应该由用户输入或根据自由度查询表
DEFAULT_T_FACTOR = 1.0
# 均匀分布的系数
K_UNIFORM = math.sqrt(3)
# 三角形分布的系数
K_TRIANGULAR = math.sqrt(6)
# 正态分布，置信水平为95%
K_NORMAL_DISTRIBUTION = 2 # 可以根据需要调整

def custom_round_decimal(number: float, decimals: int) -> float:
    """
    使用 decimal 模块实现“四舍六入五成双”并包含“5后若有数字就入”的舍入规则。
    
    Args:
        number (float): 待舍入的数字。
        decimals (int): 小数点后保留的位数。
    Returns:
        float: 舍入后的数字。
    """
    if decimals < 0:
        raise ValueError("decimals 必须是非负整数。")
    
    # 1. 将浮点数转换为 Decimal，避免浮点数精度问题。使用 str(number) 是为了避免二进制浮点数转换误差。
    d_num_str = str(number)
    d_num = Decimal(d_num_str)

    # 2. 构造一个代表所需精度的 Decimal 对象，例如 '0.01' 用于两位小数
    if decimals == 0:
        quantize_to = Decimal('1')
    else:
        # 创建一个精确到 decimals 位的 Decimal，例如 Decimal('0.001') for decimals=3
        quantize_to = Decimal('1e-{}'.format(decimals))

    # 3. 检查舍入位及其之后是否有非零数字
    # 获取数字的字符串表示，并确保小数点后有足够的位数进行判断
    dot_index = d_num_str.find('.')
    if dot_index == -1: # 如果是整数，直接返回，不需要小数舍入
        return float(d_num)

    # 确保字符串有足够的长度来检查舍入位
    # 需要检查的数字在小数点后 decimals + 1 位
    required_length_after_dot = decimals + 1
    current_length_after_dot = len(d_num_str) - dot_index - 1
    
    # 如果当前小数位数不足以达到舍入位，则认为其后都是0，不需要特殊处理
    if current_length_after_dot < required_length_after_dot:
        # 直接使用 ROUND_HALF_EVEN 对原始 Decimal 进行量化
        return float(d_num.quantize(quantize_to, rounding=ROUND_HALF_EVEN))


    # 提取舍入位（decimals + 1 位）的数字
    # 例如：1.2345, decimals=2, target_digit_index = dot_index + 2 + 1 = 4
    target_digit_index_in_str = dot_index + required_length_after_dot
    
    digit_to_check_char = d_num_str[target_digit_index_in_str]
    digit_to_check = int(digit_to_check_char)

    # 检查 5 后面是否有非零数字
    # 例如 1.2351 -> "1", 1.2350 -> ""
    rest_of_digits_str = d_num_str[target_digit_index_in_str + 1:].strip('0')
    has_non_zero_after_five = bool(rest_of_digits_str)

    # 4. 根据规则进行舍入
    if digit_to_check < 5:
        # 四舍：直接向下舍入
        return float(d_num.quantize(quantize_to, rounding=ROUND_HALF_DOWN))
    elif digit_to_check > 5:
        # 六入：直接向上舍入
        return float(d_num.quantize(quantize_to, rounding=ROUND_HALF_UP))
    else: # digit_to_check == 5
        if has_non_zero_after_five:
            # 5后有数字，直接进位
            return float(d_num.quantize(quantize_to, rounding=ROUND_HALF_UP))
        else:
            # 5后无数字（或只有0），应用“五成双”
            return float(d_num.quantize(quantize_to, rounding=ROUND_HALF_EVEN))

# --- 单个物理量不确定度计算函数 ---

def calculate_b_uncertainty_from_limit(uncertainty_limit: float, distribution_type: str) -> float:
    """
    根据仪器的不确定度限值计算B类不确定度。
    通常用于多次测量中仪器的不确定度。
    Args:
        uncertainty_limit (float): 仪器的不确定度限值。
        distribution_type (str): 分布类型 ('均匀分布', '正态分布', '三角形分布')。
    Returns:
        float: B类不确定度 u_B。
    """
    if distribution_type == '均匀分布':
        return uncertainty_limit / K_UNIFORM
    elif distribution_type == '正态分布':
        return uncertainty_limit / K_NORMAL_DISTRIBUTION 
    elif distribution_type == '三角形分布':
        return uncertainty_limit / K_TRIANGULAR
    else:
        raise ValueError("无效的分布类型。请选择 '均匀分布', '正态分布' 或 '三角形分布'。")


def calculate_combined_uncertainty(u_a: float, u_b: float) -> float:
    """
    计算合成不确定度。
    Args:
        u_a (float): A类不确定度。
        u_b (float): B类不确定度。
    Returns:
        float: 合成不确定度 u_x。
    """
    return math.sqrt(u_a**2 + u_b**2)

# --- 多次测量A类不确定度计算函数 ---

def calculate_a_uncertainty_multiple_measurements(data_list: list[float], t_factor: float = DEFAULT_T_FACTOR) -> tuple[float, float, float]:
    """
    计算多次测量下的A类不确定度。
    Args:
        data_list (list[float]): 测量数据列表。
        t_factor (float): t因子。
    Returns:
        tuple[float, float, float]: (平均值, A类不确定度 u_A, 实验标准差 S_x)
    """
    if not data_list:
        raise ValueError("数据列表不能为空。")
    
    n = len(data_list)
    mean_val = np.mean(data_list)
    
    if n < 2: # 至少需要两个数据点才能计算标准差
        # 如果只有一个数据点，实验标准差无法计算，A类不确定度为0
        # 实际情况可能需要提示用户输入更多数据或考虑为单次测量
        return mean_val, 0.0, 0.0
        
    s_x = np.std(data_list, ddof=1) # 样本标准差 (ddof=1 表示除以 n-1)
    u_a_prime = s_x / math.sqrt(n) # 平均值的标准不确定度
    
    u_a = t_factor * u_a_prime # 扩展不确定度或修正后的A类不确定度

    return mean_val, u_a, s_x


# --- 不确定度传递函数 ---

def propagate_uncertainty(function_str: str, x_values: dict[str, float], u_x_values: dict[str, float]) -> tuple[float, float]:
    """
    计算不确定度传递。
    Args:
        function_str (str): output物理量y与input物理量x_1, ..., x_n之间的函数关系字符串。
                             例如: 'x1*x2 + sin(x3)'
        x_values (dict): input物理量的测量值字典，键为变量名，值为测量值。
                         例如: {'x1': 10.0, 'x2': 2.0, 'x3': 0.5}
        u_x_values (dict): input物理量相应的不确定度字典，键为变量名，值为不确定度。
                           例如: {'x1': 0.1, 'x2': 0.05, 'x3': 0.01}
    Returns:
        tuple[float, float]: (output物理量的测量值 y_value, output物理量的不确定度 u_y)
    """
    if not function_str:
        raise ValueError("函数表达式不能为空。")
    if not x_values:
        raise ValueError("输入物理量测量值不能为空。")
    if not u_x_values:
        raise ValueError("输入物理量不确定度不能为空。")

    # 1. 定义符号变量
    symbols = []
    for var_name in x_values.keys():
        symbols.append(sympy.Symbol(var_name))

    # 2. 将函数字符串转换为 SymPy 表达式
    try:
        expr = sympy.sympify(function_str)
    except (sympy.SympifyError, SyntaxError) as e:
        raise ValueError(f"函数表达式无效: {e}")

    # 3. 计算 output 物理量的测量值 y_value
    # 将字典的键转换为 SymPy 符号，值保持不变
    subs_dict = {sympy.Symbol(k): v for k, v in x_values.items()}
    y_value = float(expr.subs(subs_dict))

    # 4. 计算不确定度 u_y
    sum_of_squares = 0.0
    for var_name in x_values.keys():
        sym_var = sympy.Symbol(var_name)
        if sym_var not in expr.free_symbols:
            # 如果变量不在表达式中，其偏导数为0，跳过
            continue

        # 计算偏导数
        partial_derivative_expr = sympy.diff(expr, sym_var)

        # 代入数值
        partial_derivative_value = float(partial_derivative_expr.subs(subs_dict))

        # 获取对应变量的不确定度
        u_xi = u_x_values.get(var_name)
        if u_xi is None:
            raise ValueError(f"缺少变量 '{var_name}' 的不确定度。")

        sum_of_squares += (partial_derivative_value * u_xi)**2

    u_y = math.sqrt(sum_of_squares)

    return y_value, u_y

# --- 辅助函数：尝试将字符串转换为浮点数列表 ---
def parse_float_list(data_str: str) -> list[float]:
    """
    将字符串（如 '1.2, 3.4, 5.6' 或 '1.2 3.4 5.6'）解析为浮点数列表。
    """
    # 替换中文逗号和全角空格
    data_str = data_str.replace('，', ',').replace('　', ' ')
    # 尝试用逗号分割，如果只有一个元素，再尝试用空格分割
    elements = [e.strip() for e in data_str.split(',') if e.strip()]
    if len(elements) == 1 and ' ' in elements[0]:
        elements = [e.strip() for e in elements[0].split(' ') if e.strip()]
    
    if not elements:
        return []

    float_list = []
    for elem in elements:
        try:
            float_list.append(float(elem))
        except ValueError:
            raise ValueError(f"数据列表中包含非数字项: '{elem}'。请确保输入的是有效的数字。")
    return float_list

# 重要的格式化函数
def format_uncertainty_and_value(value: float, uncertainty: float) -> tuple[str, str]:
    """
    根据国际惯例格式化不确定度和测量值：
    1. 不确定度保留两位有效数字。
    2. 测量值的小数点后位数与不确定度相同，并采用“四舍六入五成双”及“5后若有数字就入”的舍入规则。
    """
    if uncertainty == 0:
        # 如果不确定度为0，则测量值可以保留固定位数，这里假设为4位小数
        return f"{value:.4f}", f"{uncertainty:.2g}"

    # 1. 格式化不确定度为两位有效数字
    formatted_uncertainty_str = f"{uncertainty:.2g}"
    
    # 2. 确定不确定度的小数点后位数
    decimal_places_uncertainty = 0
    try:
        # 使用Decimal进行精确转换，避免浮点数精度问题影响字符串解析
        d_unc = Decimal(formatted_uncertainty_str)
        s_d_unc = str(d_unc) # 再次转为字符串以便查找小数点和指数

        if 'E' in s_d_unc.upper(): # 处理科学计数法，例如 "1.5E-03"
            e_idx = s_d_unc.upper().find('E')
            mantissa_part = s_d_unc[:e_idx] # 尾数部分，例如 "1.5"
            exponent_str = s_d_unc[e_idx+1:] # 指数部分，例如 "-03"
            
            exponent = int(exponent_str)

            dot_idx_mantissa = mantissa_part.find('.')
            if dot_idx_mantissa != -1:
                mantissa_decimals = len(mantissa_part) - dot_idx_mantissa - 1
            else:
                mantissa_decimals = 0 # 整数尾数

            # 最终小数点位数 = 尾数小数位数 - 指数
            # 例如 1.5e-3 -> mantissa_decimals=1, exponent=-3 -> 1 - (-3) = 4
            # 例如 15e-3 (等同于1.5e-2) -> mantissa_decimals=0, exponent=-3 -> 0 - (-3) = 3
            decimal_places_uncertainty = mantissa_decimals - exponent 
            
            # 例如 1.2e+02 (120) -> mantissa_decimals=1, exponent=2 -> 1 - 2 = -1，取max(0, -1) = 0
            decimal_places_uncertainty = max(0, decimal_places_uncertainty)

        elif '.' in s_d_unc: # 非科学计数法，例如 "0.0015"
            decimal_places_uncertainty = len(s_d_unc.split('.')[1])
        else: # 整数，例如 "23"
            decimal_places_uncertainty = 0

    except Exception:
        # 如果解析失败，退回到一个默认值（例如4位小数），并打印警告
        decimal_places_uncertainty = 4 # 安全默认值
        print(f"警告: 无法精确确定不确定度 '{formatted_uncertainty_str}' 的小数点位数，将使用默认 {decimal_places_uncertainty} 位。")


    # 3. 使用 custom_round_decimal 舍入测量值到指定的小数位数
    formatted_value_float = custom_round_decimal(value, decimal_places_uncertainty)
    
    # 4. 确保格式化后的测量值字符串精确到指定的小数位数
    # 注意：f-string {:.nf} 会进行标准的ROUND_HALF_EVEN舍入，
    # 但我们已经通过 custom_round_decimal 完成了所需的舍入，
    # 这里只是为了确保输出字符串的位数正确。
    formatted_value_str = f"{formatted_value_float:.{decimal_places_uncertainty}f}"

    return formatted_value_str, formatted_uncertainty_str