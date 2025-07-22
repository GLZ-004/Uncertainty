import customtkinter as ctk
from tkinter import messagebox, filedialog
from calculation_formulas import propagate_uncertainty, parse_float_list
import os # 用于文件操作

class UncertaintyPropagationCalculator(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance

        self.grid_columnconfigure((0, 1), weight=1)
        # 为更多的行设置权重，以更好地布局
        for i in range(10): 
            self.grid_rowconfigure(i, weight=1)

        self.input_vars_count = 1 # 初始输入物理量数量
        self.input_var_entries = [] # 存储输入物理量值和不确定度的Entry widgets

        self.create_widgets()

    def create_widgets(self):
        # 标题
        self.title_label = ctk.CTkLabel(self, text="不确定度的传递", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # 返回按钮
        self.back_button = ctk.CTkButton(self, text="返回主菜单", command=self.app.create_main_menu)
        self.back_button.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # 函数关系输入
        self.function_label = ctk.CTkLabel(self, text="函数关系 y = f(x1, x2, ...):", font=("Arial", 16))
        self.function_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.function_entry = ctk.CTkEntry(self, placeholder_text="例如: x1*x2 + sin(x3)", width=400)
        self.function_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # 动态输入变量区域
        self.input_vars_frame = ctk.CTkScrollableFrame(self, label_text="输入物理量 (x, ux)", height=200)
        self.input_vars_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.input_vars_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 添加/移除变量按钮
        self.add_var_button = ctk.CTkButton(self, text="添加物理量", command=self.add_input_variable)
        self.add_var_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.remove_var_button = ctk.CTkButton(self, text="移除物理量", command=self.remove_input_variable)
        self.remove_var_button.grid(row=3, column=1, padx=10, pady=5, sticky="e")

        # 初始化输入变量
        self.render_input_variables()

        # 计算按钮
        self.calculate_button = ctk.CTkButton(self, text="计算传递不确定度", command=self.perform_propagation_calculation, font=("Arial", 18))
        self.calculate_button.grid(row=4, column=0, columnspan=2, pady=20)

        # 结果显示区域
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        self.result_frame.grid_columnconfigure((0, 1), weight=1)

        self.result_value_label = ctk.CTkLabel(self.result_frame, text="输出测量值 (y): ", font=("Arial", 18, "bold"))
        self.result_value_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.result_uncertainty_label = ctk.CTkLabel(self.result_frame, text="输出不确定度 (uy): ", font=("Arial", 18, "bold"))
        self.result_uncertainty_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # 导入/导出功能
        self.io_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.io_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.io_frame.grid_columnconfigure((0, 1), weight=1)

        self.import_button = ctk.CTkButton(self.io_frame, text="导入配置", command=self.import_config)
        self.import_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.export_button = ctk.CTkButton(self.io_frame, text="导出配置", command=self.export_config)
        self.export_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")


    def render_input_variables(self):
        """重新渲染所有输入物理量的Entry"""
        # 清除旧的 Entry
        for widgets in self.input_var_entries:
            for widget in widgets:
                widget.destroy()
        self.input_var_entries.clear()

        for i in range(self.input_vars_count):
            row_num = i 
            
            # 变量名 (只读，显示 x1, x2, ...)
            var_name_label = ctk.CTkLabel(self.input_vars_frame, text=f"x{i+1}:", font=("Arial", 14))
            var_name_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")

            # 测量值 Entry
            value_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"x{i+1} 测量值", width=100)
            value_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")

            # 不确定度 Entry
            uncertainty_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"ux{i+1} 不确定度", width=100)
            uncertainty_entry.grid(row=row_num, column=2, padx=5, pady=5, sticky="ew")
            
            self.input_var_entries.append([var_name_label, value_entry, uncertainty_entry])


    def add_input_variable(self):
        self.input_vars_count += 1
        self.render_input_variables() # 重新渲染UI

    def remove_input_variable(self):
        if self.input_vars_count > 1: # 至少保留一个变量
            self.input_vars_count -= 1
            self.render_input_variables() # 重新渲染UI
        else:
            messagebox.showwarning("警告", "至少需要一个输入物理量。")

    def perform_propagation_calculation(self):
        try:
            function_str = self.function_entry.get().strip()
            if not function_str:
                raise ValueError("函数表达式不能为空。")

            x_values = {}
            u_x_values = {}

            for i, entries in enumerate(self.input_var_entries):
                # entries[1] 是测量值 Entry, entries[2] 是不确定度 Entry
                var_name = f"x{i+1}"
                
                # 检查 Entry 是否存在且未被销毁
                if not entries[1].winfo_exists() or not entries[2].winfo_exists():
                    raise ValueError(f"物理量 {var_name} 的输入框已被销毁，请重新输入。")

                x_str = entries[1].get().strip()
                ux_str = entries[2].get().strip()

                if not x_str or not ux_str:
                    raise ValueError(f"物理量 {var_name} 的测量值和不确定度不能为空。")
                
                try:
                    x_values[var_name] = float(x_str)
                    u_x_values[var_name] = float(ux_str)
                except ValueError:
                    raise ValueError(f"物理量 {var_name} 的测量值或不确定度必须是有效数字。")

            if not x_values:
                raise ValueError("请至少添加一个输入物理量。")

            # 调用核心计算函数
            y_value, u_y = propagate_uncertainty(function_str, x_values, u_x_values)

            self.result_value_label.configure(text=f"输出测量值 (y): {y_value:.4g}")
            self.result_uncertainty_label.configure(text=f"输出不确定度 (uy): {u_y:.2g}")

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("计算错误", f"发生未知错误: {e}")

    def import_config(self):
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) < 2:
                        raise ValueError("文件内容格式不正确。")
                    
                    # 读取函数表达式
                    self.function_entry.delete(0, ctk.END)
                    self.function_entry.insert(0, lines[0].strip())

                    # 读取输入物理量
                    input_data = []
                    for line in lines[1:]:
                        parts = [p.strip() for p in line.strip().split(',')]
                        if len(parts) == 2:
                            input_data.append((parts[0], parts[1]))
                        else:
                            raise ValueError(f"物理量行格式不正确: {line.strip()}")
                    
                    self.input_vars_count = len(input_data)
                    self.render_input_variables() # 重新渲染UI以匹配数量

                    for i, (value_str, uncertainty_str) in enumerate(input_data):
                        if i < len(self.input_var_entries):
                            self.input_var_entries[i][1].delete(0, ctk.END) # value entry
                            self.input_var_entries[i][1].insert(0, value_str)
                            self.input_var_entries[i][2].delete(0, ctk.END) # uncertainty entry
                            self.input_var_entries[i][2].insert(0, uncertainty_str)
                        else:
                            messagebox.showwarning("警告", "导入的物理量数量超过当前UI的限制，部分物理量未导入。")
                            break

                messagebox.showinfo("导入成功", "配置已成功导入。")
            except Exception as e:
                messagebox.showerror("导入失败", f"无法导入配置文件: {e}")

    def export_config(self):
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 写入函数表达式
                    f.write(self.function_entry.get().strip() + "\n")
                    
                    # 写入每个输入物理量的值和不确定度
                    for i, entries in enumerate(self.input_var_entries):
                        if entries[1].winfo_exists() and entries[2].winfo_exists():
                            value = entries[1].get().strip()
                            uncertainty = entries[2].get().strip()
                            f.write(f"{value},{uncertainty}\n")
                        else:
                            messagebox.showwarning("警告", f"物理量 x{i+1} 的输入框已销毁，未导出。")

                messagebox.showinfo("导出成功", f"配置已成功导出到 {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("导出失败", f"无法导出配置文件: {e}")