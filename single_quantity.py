import customtkinter as ctk
from tkinter import messagebox
from calculation_formulas import (
    calculate_b_uncertainty_from_limit,
    calculate_a_uncertainty_multiple_measurements,
    calculate_combined_uncertainty,
    parse_float_list
)
import math # 确保导入了 math

class SingleQuantityCalculator(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        self.grid_columnconfigure((0, 1), weight=1)
        # 增加一些行权重，确保内容居中或合理分布
        for i in range(10): # 调整行数以适应内容
            self.grid_rowconfigure(i, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # ... (这部分保持不变) ...
        self.title_label = ctk.CTkLabel(self, text="单个物理量不确定度计算与合成", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        self.back_button = ctk.CTkButton(self, text="返回主菜单", command=self.app.create_main_menu)
        self.back_button.grid(row=0, column=1, padx=10, pady=10, sticky="ne") 

        self.measurement_type_label = ctk.CTkLabel(self, text="选择测量类型:", font=("Arial", 16))
        self.measurement_type_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.measurement_type_var = ctk.StringVar(value="单次测量")
        self.single_measurement_radio = ctk.CTkRadioButton(
            self, text="单次测量", variable=self.measurement_type_var, value="单次测量", command=self.show_measurement_options
        )
        self.single_measurement_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.multiple_measurement_radio = ctk.CTkRadioButton(
            self, text="多次测量", variable=self.measurement_type_var, value="多次测量", command=self.show_measurement_options
        )
        self.multiple_measurement_radio.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.measurement_options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.measurement_options_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.measurement_options_frame.grid_columnconfigure((0, 1), weight=1)

        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        self.result_frame.grid_columnconfigure((0, 1), weight=1)

        self.result_value_label = ctk.CTkLabel(self.result_frame, text="测量值: ", font=("Arial", 18, "bold"))
        self.result_value_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.result_uncertainty_label = ctk.CTkLabel(self.result_frame, text="不确定度: ", font=("Arial", 18, "bold"))
        self.result_uncertainty_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.show_measurement_options()

        # 计算按钮 (移到最后，确保在 show_measurement_options 之后创建，且在 perform_calculation 中不会被销毁)
        self.calculate_button = ctk.CTkButton(self, text="计算", command=self.perform_calculation, font=("Arial", 18))
        # 确保 calculate_button 的 grid row 不会被其他元素覆盖，或者确保它在 show_measurement_options 之后设置
        # 这里设置为一个较高的固定行，例如 row=9，假设前面最多用到row=8
        self.calculate_button.grid(row=9, column=0, columnspan=2, pady=20)


    def clear_measurement_options_frame(self):
        for widget in self.measurement_options_frame.winfo_children():
            widget.destroy()

    def show_measurement_options(self):
        self.clear_measurement_options_frame()
        measurement_type = self.measurement_type_var.get()

        row_idx = 0

        # 通用输入：仪器的不确定度限值, 最小分度值, 分布类型
        # 这些输入框需要定义在 self 而不是 self.measurement_options_frame 内部，
        # 或者至少确保它们不会被销毁。为了简洁，我们让它们总是存在。
        # 重新组织一下，让所有共同的输入框不被清除函数销毁。
        
        # 考虑到代码结构，将这些通用输入也放在 measurement_options_frame 中
        # 但是在 destroy() 之前，我们需要确保所有需要引用的 Entry 都有一个 self. 引用

        # 定义 Entry 的局部变量以避免引用已销毁的对象
        self.entry_widgets = {} # 用字典存储所有可能动态创建的 Entry widgets

        if measurement_type == "单次测量":
            self.single_measurement_type_label = ctk.CTkLabel(self.measurement_options_frame, text="单次测量类型:", font=("Arial", 16))
            self.single_measurement_type_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            
            self.single_measurement_type_var = ctk.StringVar(value="一般测量")
            self.general_measurement_radio = ctk.CTkRadioButton(
                self.measurement_options_frame, text="一般测量", variable=self.single_measurement_type_var, value="一般测量", command=self.show_single_measurement_details
            )
            self.general_measurement_radio.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1
            
            self.ruler_measurement_radio = ctk.CTkRadioButton(
                self.measurement_options_frame, text="直尺类测量", variable=self.single_measurement_type_var, value="直尺类测量", command=self.show_single_measurement_details
            )
            self.ruler_measurement_radio.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1

            self.single_measurement_details_frame = ctk.CTkFrame(self.measurement_options_frame, fg_color="transparent")
            self.single_measurement_details_frame.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", pady=10)
            self.single_measurement_details_frame.grid_columnconfigure((0, 1), weight=1)
            row_idx += 1

            self.show_single_measurement_details() # 初始显示一般测量详情

            self.reading_factor_label = ctk.CTkLabel(self.measurement_options_frame, text="估读情况 (Δx/Δ):", font=("Arial", 16))
            self.reading_factor_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.reading_factor_combobox = ctk.CTkComboBox(
                self.measurement_options_frame, values=["1/10", "1/5", "1/2", "1"], state="readonly", width=120
            )
            self.reading_factor_combobox.set("1/10")
            self.reading_factor_combobox.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1

            # 仪器的最小分度值 (Δ)
            self.min_division_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的最小分度值 (Δ):", font=("Arial", 16))
            self.min_division_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['min_division'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['min_division'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1
            
            # 仪器的不确定度限值 (U_A) - 单次测量也可能需要
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值 (U_A):", font=("Arial", 16))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1


        elif measurement_type == "多次测量":
            # 测量数据列表
            self.data_list_label = ctk.CTkLabel(self.measurement_options_frame, text="测量数据 (逗号或空格分隔):", font=("Arial", 16))
            self.data_list_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['data_list'] = ctk.CTkEntry(self.measurement_options_frame, width=250)
            self.entry_widgets['data_list'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
            row_idx += 1

            # t因子
            self.t_factor_label = ctk.CTkLabel(self.measurement_options_frame, text="t因子 (默认1):", font=("Arial", 16))
            self.t_factor_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['t_factor'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['t_factor'].insert(0, "1.0")
            self.entry_widgets['t_factor'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1
            
            # 仪器的不确定度限值 (U_A)
            self.instrument_uncertainty_limit_label = ctk.CTkLabel(self.measurement_options_frame, text="仪器的不确定度限值 (U_A):", font=("Arial", 16))
            self.instrument_uncertainty_limit_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['instrument_uncertainty_limit'] = ctk.CTkEntry(self.measurement_options_frame, width=120)
            self.entry_widgets['instrument_uncertainty_limit'].grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
            row_idx += 1


        # 分布类型
        self.distribution_type_label = ctk.CTkLabel(self.measurement_options_frame, text="分布类型:", font=("Arial", 16))
        self.distribution_type_label.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        self.distribution_type_combobox = ctk.CTkComboBox(
            self.measurement_options_frame, values=["均匀分布", "正态分布", "三角形分布"], state="readonly", width=120
        )
        self.distribution_type_combobox.set("均匀分布")
        self.distribution_type_combobox.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
        row_idx += 1


    def show_single_measurement_details(self):
        for widget in self.single_measurement_details_frame.winfo_children():
            widget.destroy()

        single_measurement_type = self.single_measurement_type_var.get()

        if single_measurement_type == "一般测量":
            self.measurement_value_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 (仅一个数据):", font=("Arial", 16))
            self.measurement_value_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['measurement_value'] = ctk.CTkEntry(self.single_measurement_details_frame, width=120)
            self.entry_widgets['measurement_value'].grid(row=0, column=1, padx=5, pady=5, sticky="w")
        elif single_measurement_type == "直尺类测量":
            self.measurement_value1_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 1:", font=("Arial", 16))
            self.measurement_value1_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['measurement_value1'] = ctk.CTkEntry(self.single_measurement_details_frame, width=120)
            self.entry_widgets['measurement_value1'].grid(row=0, column=1, padx=5, pady=5, sticky="w")

            self.measurement_value2_label = ctk.CTkLabel(self.single_measurement_details_frame, text="测量值 2:", font=("Arial", 16))
            self.measurement_value2_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.entry_widgets['measurement_value2'] = ctk.CTkEntry(self.single_measurement_details_frame, width=120)
            self.entry_widgets['measurement_value2'].grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def get_float_input(self, key, name):
        """从 self.entry_widgets 字典中获取Entry并尝试转换为浮点数"""
        entry_widget = self.entry_widgets.get(key)
        if not entry_widget or not entry_widget.winfo_exists(): # 检查组件是否存在
            raise ValueError(f"'{name}' 输入框未找到或已销毁。")
        try:
            return float(entry_widget.get())
        except ValueError:
            raise ValueError(f"'{name}' 必须是有效的数字。")

    def get_float_list_input(self, key, name):
        """从 self.entry_widgets 字典中获取Entry并尝试解析为浮点数列表"""
        entry_widget = self.entry_widgets.get(key)
        if not entry_widget or not entry_widget.winfo_exists(): # 检查组件是否存在
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

            self.result_value_label.configure(text=f"测量值: {final_measurement_value:.4g}")
            self.result_uncertainty_label.configure(text=f"不确定度: {final_uncertainty:.2g}")

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            # 捕获所有其他异常，包括 invalid command name
            messagebox.showerror("计算错误", f"发生未知错误: {e}")