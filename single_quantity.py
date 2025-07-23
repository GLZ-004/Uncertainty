import customtkinter as ctk
from tkinter import messagebox
from calculation_formulas import (
    calculate_b_uncertainty_from_limit,
    calculate_a_uncertainty_multiple_measurements,
    calculate_combined_uncertainty,
    parse_float_list,
    format_uncertainty_and_value
)
import math

# 如果要使用图片图标，请取消注释并确保图片文件存在
# from PIL import Image
# BACK_ICON_PATH = "icons/back_arrow.png" # 假设图标在 icons 文件夹下

class SingleQuantityCalculator(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent")
        self.app = app_instance

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 优化行权重，确保内容合理分布和居中
        self.grid_rowconfigure(0, weight=0) # 标题和返回按钮
        self.grid_rowconfigure(1, weight=0) # 选择测量类型
        self.grid_rowconfigure(2, weight=0) # 多次测量radio
        self.grid_rowconfigure(3, weight=0) # 测量选项动态框架
        self.grid_rowconfigure(4, weight=0) # 估读情况
        self.grid_rowconfigure(5, weight=0) # 最小分度值
        self.grid_rowconfigure(6, weight=0) # 不确定度限值
        self.grid_rowconfigure(7, weight=0) # 分布类型 (通用)
        self.grid_rowconfigure(8, weight=1) # 弹性空间，推Results和Button到底部
        self.grid_rowconfigure(9, weight=0) # 结果显示
        self.grid_rowconfigure(10, weight=0) # 计算按钮
        self.grid_rowconfigure(11, weight=1) # 底部弹性空间，确保内容不贴边

        self.entry_widgets = {}

        self.create_widgets()
        self.show_measurement_options() # 确保初始时显示正确的测量选项

    def create_widgets(self):
        # 标题
        self.title_label = ctk.CTkLabel(self, text="单个物理量不确定度计算与合成", font=("Arial", 30, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(25, 15), sticky="n")

        # 返回按钮 - 文本加上箭头符号
        # 如果使用图片图标，可以这样加载:
        # back_icon = ctk.CTkImage(light_image=Image.open(BACK_ICON_PATH),
        #                          dark_image=Image.open(BACK_ICON_PATH), size=(18, 18))
        self.back_button = ctk.CTkButton(
            self, 
            text="← 返回主菜单", # 添加箭头符号
            # image=back_icon, # 如果使用图片图标，取消注释此行
            command=self.app.create_main_menu,
            width=120, # 按钮宽度增加
            height=35, # 按钮高度增加
            font=("Arial", 15, "bold"), # 字体更清晰
            corner_radius=9, # 稍大的圆角
            fg_color="transparent", # 透明背景
            text_color=("blue", "lightblue") # 蓝色文本，像一个链接
        )
        self.back_button.grid(row=0, column=1, padx=25, pady=(25, 15), sticky="ne")

        # --- 测量类型选择 ---
        self.measurement_type_label = ctk.CTkLabel(self, text="选择测量类型:", font=("Arial", 16, "bold"))
        self.measurement_type_label.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="w")
        
        self.measurement_type_var = ctk.StringVar(value="单次测量")
        self.single_measurement_radio = ctk.CTkRadioButton(
            self, text="单次测量", variable=self.measurement_type_var, value="单次测量", 
            command=self.show_measurement_options, font=("Arial", 16)
        )
        self.single_measurement_radio.grid(row=1, column=1, padx=20, pady=(15, 5), sticky="w")
        
        self.multiple_measurement_radio = ctk.CTkRadioButton(
            self, text="多次测量", variable=self.measurement_type_var, value="多次测量", 
            command=self.show_measurement_options, font=("Arial", 16)
        )
        self.multiple_measurement_radio.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        # --- 测量选项动态框架 ---
        # 放置在第3行，方便管理内部组件的动态销毁和创建
        self.measurement_options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.measurement_options_frame.grid(row=3, column=0, columnspan=2, padx=30, pady=10, sticky="nsew")
        self.measurement_options_frame.grid_columnconfigure(0, weight=1)
        self.measurement_options_frame.grid_columnconfigure(1, weight=1)

        # --- 结果显示区域 ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=9, column=0, columnspan=2, padx=30, pady=(20, 10), sticky="ew")
        self.result_frame.grid_columnconfigure((0, 1), weight=1)

        self.result_value_label = ctk.CTkLabel(self.result_frame, text="测量值: ", font=("Arial", 22, "bold")) # 字号更大
        self.result_value_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.result_uncertainty_label = ctk.CTkLabel(self.result_frame, text="不确定度: ", font=("Arial", 22, "bold")) # 字号更大
        self.result_uncertainty_label.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        # --- 计算按钮 ---
        self.calculate_button = ctk.CTkButton(
            self, 
            text="计算", 
            command=self.perform_calculation, 
            font=("Arial", 22, "normal"), 
            height=55, # 按钮更高
            width=220, # 按钮更宽
            corner_radius=12 # 增加圆角
        )
        self.calculate_button.grid(row=10, column=0, columnspan=2, pady=(15, 40))


    def clear_measurement_options_frame(self):
        for widget in self.measurement_options_frame.winfo_children():
            widget.destroy()
        self.entry_widgets.clear()

    def show_measurement_options(self):
        self.clear_measurement_options_frame()
        measurement_type = self.measurement_type_var.get()

        row_idx = 0

        if measurement_type == "单次测量":
            # --- 单次测量类型选择 ---
            self.single_measurement_type_label = ctk.CTkLabel(self.measurement_options_frame, text="单次测量类型:", font=("Arial", 15))
            self.single_measurement_type_label.grid(row=row_idx, column=0, padx=10, pady=(10,0), sticky="w")
            
            self.single_measurement_type_var = ctk.StringVar(value="一般测量")
            self.general_measurement_radio = ctk.CTkRadioButton(
                self.measurement_options_frame, text="一般测量", variable=self.single_measurement_type_var, value="一般测量", 
                command=self.show_single_measurement_details, font=("Arial", 15)
            )
            self.general_measurement_radio.grid(row=row_idx, column=1, padx=10, pady=(10,0), sticky="w")
            row_idx += 1
            
            self.ruler_measurement_radio = ctk.CTkRadioButton(
                self.measurement_options_frame, text="直尺类测量", variable=self.single_measurement_type_var, value="直尺类测量", 
                command=self.show_single_measurement_details, font=("Arial", 15)
            )
            self.ruler_measurement_radio.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            row_idx += 1

            # --- 单次测量详情动态框架 ---
            self.single_measurement_details_frame = ctk.CTkFrame(self.measurement_options_frame, fg_color="transparent")
            self.single_measurement_details_frame.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=5)
            self.single_measurement_details_frame.grid_columnconfigure(0, weight=1)
            self.single_measurement_details_frame.grid_columnconfigure(1, weight=1)
            row_idx += 1

            self.show_single_measurement_details() # 初始显示一般测量详情

            # --- 估读情况 ---
            self.reading_factor_label = ctk.CTkLabel(self.measurement_options_frame, text="估读情况 (Δx/Δ):", font=("Arial", 15))
            self.reading_factor_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.reading_factor_combobox = ctk.CTkComboBox(
                self.measurement_options_frame, values=["1/10", "1/5", "1/2", "1"], state="readonly", width=180, height=32, font=("Arial", 15)
            )
            self.reading_factor_combobox.set("1/10")
            self.reading_factor_combobox.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            row_idx += 1

            # --- 仪器的最小分度值 (Δ) ---
            self.min_division_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的最小分度值 (Δ):", font=("Arial", 15))
            self.min_division_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['min_division'] = ctk.CTkEntry(self.measurement_options_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['min_division'].grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            row_idx += 1
            
<<<<<<< HEAD
            # 仪器的不确定度限值 (for U_B2) - 单次测量也可能需要
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值:", font=("Arial", 16))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
=======
            # --- 仪器的不确定度限值 (for U_B2) ---
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值:", font=("Arial", 15))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
>>>>>>> dev
            row_idx += 1


        elif measurement_type == "多次测量":
            # --- 测量数据列表 ---
            self.data_list_label = ctk.CTkLabel(self.measurement_options_frame, text="测量数据 (逗号或空格分隔):", font=("Arial", 15))
            self.data_list_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['data_list'] = ctk.CTkEntry(self.measurement_options_frame, width=280, height=32, font=("Arial", 15))
            self.entry_widgets['data_list'].grid(row=row_idx, column=1, padx=10, pady=5, sticky="ew")
            row_idx += 1

            # --- t因子 ---
            self.t_factor_label = ctk.CTkLabel(self.measurement_options_frame, text="t因子 (默认1):", font=("Arial", 15))
            self.t_factor_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['t_factor'] = ctk.CTkEntry(self.measurement_options_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['t_factor'].insert(0, "1.0")
            self.entry_widgets['t_factor'].grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            row_idx += 1
            
<<<<<<< HEAD
            # 仪器的不确定度限值 (U_B2)
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值:", font=("Arial", 16))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
=======
            # --- 仪器的不确定度限值 (U_B2) ---
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值:", font=("Arial", 15))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
>>>>>>> dev
            row_idx += 1

        # --- 分布类型 (通用) ---
        self.distribution_type_label = ctk.CTkLabel(self.measurement_options_frame, text="分布类型:", font=("Arial", 15))
        self.distribution_type_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
        self.distribution_type_combobox = ctk.CTkComboBox(
            self.measurement_options_frame, values=["均匀分布", "正态分布", "三角形分布"], state="readonly", width=180, height=32, font=("Arial", 15)
        )
        self.distribution_type_combobox.set("均匀分布")
        self.distribution_type_combobox.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
        row_idx += 1


    def show_single_measurement_details(self):
        for widget in self.single_measurement_details_frame.winfo_children():
            widget.destroy()
        
        for key in ['measurement_value', 'measurement_value1', 'measurement_value2']:
            if key in self.entry_widgets:
                del self.entry_widgets[key]


        single_measurement_type = self.single_measurement_type_var.get()

        if single_measurement_type == "一般测量":
            self.measurement_value_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 (仅一个数据):", font=("Arial", 15))
            self.measurement_value_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['measurement_value'] = ctk.CTkEntry(self.single_measurement_details_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['measurement_value'].grid(row=0, column=1, padx=10, pady=5, sticky="w")
        elif single_measurement_type == "直尺类测量":
            self.measurement_value1_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 1:", font=("Arial", 15))
            self.measurement_value1_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['measurement_value1'] = ctk.CTkEntry(self.single_measurement_details_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['measurement_value1'].grid(row=0, column=1, padx=10, pady=5, sticky="w")

            self.measurement_value2_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 2:", font=("Arial", 15))
            self.measurement_value2_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.entry_widgets['measurement_value2'] = ctk.CTkEntry(self.single_measurement_details_frame, width=180, height=32, font=("Arial", 15))
            self.entry_widgets['measurement_value2'].grid(row=1, column=1, padx=10, pady=5, sticky="w")

    def get_float_input(self, key, name):
        """从 self.entry_widgets 字典中获取Entry并尝试转换为浮点数"""
        entry_widget = self.entry_widgets.get(key)
        if not entry_widget or not entry_widget.winfo_exists():
            raise ValueError(f"'{name}' 输入框未找到或已销毁。")
        try:
            return float(entry_widget.get())
        except ValueError:
            raise ValueError(f"'{name}' 必须是有效的数字。")

    def get_float_list_input(self, key, name):
        """从 self.entry_widgets 字典中获取Entry并尝试解析为浮点数列表"""
        entry_widget = self.entry_widgets.get(key)
        if not entry_widget or not entry_widget.winfo_exists():
            raise ValueError(f"'{name}' 输入框未找到或已销毁。")
        try:
            return parse_float_list(entry_widget.get())
        except ValueError as e:
            raise ValueError(f"'{name}' 输入有误: {e}")

    def get_reading_factor(self):
        factor_str = self.reading_factor_combobox.get()
        if '/' in factor_str:
            num, den = map(int, factor_str.split('/'))
            return num / den
        return float(factor_str)


    def perform_calculation(self):
        try:
            measurement_type = self.measurement_type_var.get()
            distribution_type = self.distribution_type_combobox.get()
            
            final_measurement_value = 0.0
            final_uncertainty = 0.0

            if measurement_type == "单次测量":
                min_division = self.get_float_input('min_division', "仪器的最小分度值")
                instrument_uncertainty_limit = self.get_float_input('instrument_uncertainty_limit', "仪器的不确定度限值")
                
                u_B2_instrument = calculate_b_uncertainty_from_limit(instrument_uncertainty_limit, distribution_type)

                reading_factor = self.get_reading_factor()
                
                single_measurement_type = self.single_measurement_type_var.get()
                
                if single_measurement_type == "一般测量":
                    measurement_value = self.get_float_input('measurement_value', "测量值")
                    final_measurement_value = measurement_value
                    
                    u_B1_reading = reading_factor * min_division
                    
                    final_uncertainty = calculate_combined_uncertainty(u_B2_instrument, u_B1_reading)
                    
                elif single_measurement_type == "直尺类测量":
                    measurement_value1 = self.get_float_input('measurement_value1', "测量值 1")
                    measurement_value2 = self.get_float_input('measurement_value2', "测量值 2")
                    final_measurement_value = abs(measurement_value2 - measurement_value1)

                    u_B_reading_single = reading_factor * min_division
                    u_B_reading_combined = math.sqrt(2 * u_B_reading_single**2) 
                    
                    final_uncertainty = calculate_combined_uncertainty(u_B2_instrument, u_B_reading_combined)

            elif measurement_type == "多次测量":
                data_list = self.get_float_list_input('data_list', "测量数据列表")
                if not data_list:
                    raise ValueError("测量数据列表不能为空。")

                t_factor = self.get_float_input('t_factor', "t因子")
                instrument_uncertainty_limit = self.get_float_input('instrument_uncertainty_limit', "仪器的不确定度限值")

                mean_val, u_A_stats, _ = calculate_a_uncertainty_multiple_measurements(data_list, t_factor)
                final_measurement_value = mean_val

                u_B_instrument = calculate_b_uncertainty_from_limit(instrument_uncertainty_limit, distribution_type)
                
                final_uncertainty = calculate_combined_uncertainty(u_A_stats, u_B_instrument)

            formatted_value, formatted_uncertainty = format_uncertainty_and_value(final_measurement_value, final_uncertainty)

            self.result_value_label.configure(text=f"测量值: {formatted_value}")
            self.result_uncertainty_label.configure(text=f"不确定度: {formatted_uncertainty}")

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("计算错误", f"发生未知错误: {e}")