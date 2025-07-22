import math
import numpy as np # 用于统计计算，需要安装 pip install numpy
import sympy # 用于符号计算和求导，需要安装 pip install sympy

# --- 常量和辅助函数 ---
# t因子，这里只是一个默认值，实际应该由用户输入或根据自由度查询表
DEFAULT_T_FACTOR = 1.0
# 均匀分布的系数
K_UNIFORM = math.sqrt(3)
# 三角形分布的系数
K_TRIANGULAR = math.sqrt(6)
# 正态分布，置信水平为95%
K_NORMAL_DISTRIBUTION = 2 # 可以根据需要调整


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