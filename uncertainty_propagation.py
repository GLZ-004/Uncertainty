import customtkinter as ctk
from tkinter import messagebox, filedialog
# 导入 calculation_formulas 模块，确保它在同一个目录下
from calculation_formulas import propagate_uncertainty, parse_float_list ,format_uncertainty_and_value
import os
import threading # 导入线程模块，用于异步计算

class UncertaintyPropagationCalculator(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance # 用于访问主应用的 after 方法等

        # 配置列权重，使其能灵活伸缩
        self.grid_columnconfigure((0, 1), weight=1)
        # 配置行权重，确保不同区域的布局合理
        self.grid_rowconfigure(0, weight=0) # 标题行
        self.grid_rowconfigure(1, weight=0) # 函数输入行
        self.grid_rowconfigure(2, weight=1) # 输入物理量滚动框 (可伸缩)
        self.grid_rowconfigure(3, weight=0) # 添加/移除按钮行
        self.grid_rowconfigure(4, weight=0) # 计算按钮行
        self.grid_rowconfigure(5, weight=0) # 结果显示行
        self.grid_rowconfigure(6, weight=0) # 导入/导出按钮行
        self.grid_rowconfigure(7, weight=0) # 符号切换按钮行
        self.grid_rowconfigure(8, weight=1) # 符号显示内容行 (当显示时，可伸缩)
        self.grid_rowconfigure(9, weight=0) # 额外行，防止内容溢出

        self.input_vars_count = 1 # 初始输入物理量数量
        self.input_var_entries = [] # 存储输入物理量值和不确定度的Entry widgets
        self.symbols_display_visible = True # 初始设为True，让第一次点击隐藏

        self.create_widgets()
        # 初始时调用一次，将符号区域折叠起来
        self.toggle_symbols_display() 

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
        self.calculate_button = ctk.CTkButton(self, text="计算传递不确定度", command=self.perform_calculation_thread, font=("Arial", 18))
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

        # --- 常用符号显示区域 ---
        self.toggle_symbols_button = ctk.CTkButton(self, text="显示常用符号 ▼", command=self.toggle_symbols_display)
        self.toggle_symbols_button.grid(row=7, column=0, columnspan=2, pady=10)

        # 关键修改：使用 CTkFrame 包裹 CTkTextbox 来实现滚动功能
        self.symbols_display_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color="gray") 
        self.symbols_display_frame.grid_columnconfigure(0, weight=1) # 使文本框能水平填充
        self.symbols_display_frame.grid_rowconfigure(0, weight=1) # 使文本框能垂直填充

        self.symbols_content_textbox = ctk.CTkTextbox(
            self.symbols_display_frame,
            wrap="word", # 单词换行
            width=700, # 设定宽度
            height=200, # 设定初始高度，让内容在默认情况下可见一部分且带滚动条
            font=("Arial", 14),
            activate_scrollbars=True # 确保滚动条自动激活
        )
        self.symbols_content_textbox.insert("0.0", self.get_common_symbols_text())
        self.symbols_content_textbox.configure(state="disabled") # 设置为只读
        self.symbols_content_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


    def get_common_symbols_text(self):
        """返回常用符号的文本描述"""
        return """
常用数学常数和函数 (基于 SymPy 语法):

常量:
  - 圆周率 π: `pi`
  - 自然底数 e: `E` 或 `exp(1)`

基本算术运算:
  - 加: `+`
  - 减: `-`
  - 乘: `*`
  - 除: `/`
  - 幂: `**` (例如: x的平方写作 `x**2`)
  - 括号: `()` 用于改变运算优先级

常用函数:
  - 平方根: `sqrt(x)` (例如: √x)
  - 绝对值: `abs(x)`
  - 自然对数: `log(x)` (以 `E` 为底)
  - 以10为底的对数: `log(x, 10)`
  - 指数函数: `exp(x)` (即 `E**x`)

三角函数 (参数为弧度):
  - 正弦: `sin(x)`
  - 余弦: `cos(x)`
  - 正切: `tan(x)`
  - 反正弦: `asin(x)`
  - 反余弦: `acos(x)`
  - 反正切: `atan(x)`

双曲函数:
  - 双曲正弦: `sinh(x)`
  - 双曲余弦: `cosh(x)`
  - 双曲正切: `tanh(x)`

示例:
  - `x1*x2 + sin(x3)`
  - `sqrt(x1**2 + x2**2)`
  - `exp(-x1/x2) * log(x3)`
"""

    def toggle_symbols_display(self):
        """切换常用符号显示区域的可见性"""
        if self.symbols_display_visible:
            # 当前可见，则隐藏
            self.symbols_display_frame.grid_forget() # 从网格中移除
            self.toggle_symbols_button.configure(text="显示常用符号 ▼")
            self.symbols_display_visible = False
        else:
            # 当前隐藏，则显示
            # 将其放置在 row=8，确保它在切换按钮下方
            self.symbols_display_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
            # 确保内部的 textbox 能够扩展填充 frame
            self.symbols_display_frame.grid_rowconfigure(0, weight=1) 
            self.symbols_display_frame.grid_columnconfigure(0, weight=1)
            self.toggle_symbols_button.configure(text="隐藏常用符号 ▲")
            self.symbols_display_visible = True

    def render_input_variables(self):
        """重新渲染所有输入物理量的Entry"""
        # 销毁旧组件时，需要先从列表中移除引用，再销毁，确保不会操作到已销毁的widget
        for label, value_entry, uncertainty_entry in self.input_var_entries:
            label.destroy()
            value_entry.destroy()
            uncertainty_entry.destroy()
        self.input_var_entries.clear()

        # 创建新组件
        for i in range(self.input_vars_count):
            row_num = i 
            
            var_name_label = ctk.CTkLabel(self.input_vars_frame, text=f"x{i+1}:", font=("Arial", 14))
            var_name_label.grid(row=row_num, column=0, padx=5, pady=5, sticky="e")

            value_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"x{i+1} 测量值", width=100)
            value_entry.grid(row=row_num, column=1, padx=5, pady=5, sticky="ew")

            uncertainty_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"ux{i+1} 不确定度", width=100)
            uncertainty_entry.grid(row=row_num, column=2, padx=5, pady=5, sticky="ew")
            
            self.input_var_entries.append([var_name_label, value_entry, uncertainty_entry])


    def add_input_variable(self):
        self.input_vars_count += 1
        self.render_input_variables()

    def remove_input_variable(self):
        if self.input_vars_count > 1:
            self.input_vars_count -= 1
            self.render_input_variables()
        else:
            messagebox.showwarning("警告", "至少需要一个输入物理量。")

    def perform_calculation_thread(self):
        """
        启动一个新线程来执行计算，并更新UI状态
        """
        # 禁用按钮，防止重复点击
        self.calculate_button.configure(state="disabled", text="计算中...")
        self.import_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.add_var_button.configure(state="disabled")
        self.remove_var_button.configure(state="disabled")
        
        # 在新线程中执行计算
        thread = threading.Thread(target=self._perform_propagation_calculation_safe)
        thread.start()

    def _perform_propagation_calculation_safe(self):
        """
        在单独线程中执行实际的计算逻辑，并通过 Tkinter 的 after 方法安全地更新 UI
        """
        try:
            # 在主线程中获取所有输入数据，然后传递给子线程，这是最安全的做法
            function_str = self.function_entry.get().strip()
            
            x_values_collected = {}
            u_x_values_collected = {}

            # 遍历 input_var_entries 收集数据
            for i, entries in enumerate(self.input_var_entries):
                var_name = f"x{i+1}"
                
                # 在获取数据前再次检查 Entry 是否存在，以防万一
                if not entries[1].winfo_exists() or not entries[2].winfo_exists():
                    # 如果任何一个输入框不存在，则抛出错误，阻止计算
                    raise ValueError(f"物理量 {var_name} 的输入框已被销毁，请重新输入。")

                x_str = entries[1].get().strip()
                ux_str = entries[2].get().strip()

                if not x_str or not ux_str:
                    raise ValueError(f"物理量 {var_name} 的测量值和不确定度不能为空。")
                
                try:
                    x_values_collected[var_name] = float(x_str)
                    u_x_values_collected[var_name] = float(ux_str)
                except ValueError:
                    raise ValueError(f"物理量 {var_name} 的测量值或不确定度必须是有效数字。")

            if not x_values_collected:
                raise ValueError("请至少添加一个输入物理量。")

            # 调用核心计算函数 (这部分是耗时的，在子线程中执行)
            y_value, u_y = propagate_uncertainty(function_str, x_values_collected, u_x_values_collected)

            # 通过 after 方法在主线程中更新 UI
            self.app.after(10, self._update_results, y_value, u_y, None)

        except ValueError as e:
            self.app.after(10, self._update_results, None, None, ("输入错误", str(e)))
        except Exception as e:
            # 捕获其他所有异常
            self.app.after(10, self._update_results, None, None, ("计算错误", f"发生未知错误: {e}"))
        finally:
            # 无论成功失败，都在主线程中重新启用按钮
            self.app.after(10, self._re_enable_buttons)

    def _update_results(self, y_value, u_y, error_info):
        """在主线程中更新结果标签或显示错误消息"""
        if error_info:
            messagebox.showerror(error_info[0], error_info[1])
        else:
            self.result_value_label.configure(text=f"输出测量值 (y): {y_value:.4g}")
            self.result_uncertainty_label.configure(text=f"输出不确定度 (uy): {u_y:.2g}")

    def _re_enable_buttons(self):
        """在主线程中重新启用所有按钮"""
        self.calculate_button.configure(state="normal", text="计算传递不确定度")
        self.import_button.configure(state="normal")
        self.export_button.configure(state="normal")
        self.add_var_button.configure(state="normal")
        self.remove_var_button.configure(state="normal")


    def import_config(self):
        """从文件导入配置"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) < 2:
                        raise ValueError("文件内容格式不正确。至少需要函数表达式和一组物理量数据。")
                    
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
                            raise ValueError(f"物理量行格式不正确: {line.strip()}。应为 '值,不确定度'。")
                    
                    self.input_vars_count = len(input_data)
                    self.render_input_variables() # 重新渲染UI以匹配数量

                    # 填充数据
                    for i, (value_str, uncertainty_str) in enumerate(input_data):
                        if i < len(self.input_var_entries): # 确保索引在范围内
                            self.input_var_entries[i][1].delete(0, ctk.END) # value entry
                            self.input_var_entries[i][1].insert(0, value_str)
                            self.input_var_entries[i][2].delete(0, ctk.END) # uncertainty entry
                            self.input_var_entries[i][2].insert(0, uncertainty_str)
                        else:
                            # 理论上 render_input_variables 已经保证了数量匹配，这里作为额外检查
                            messagebox.showwarning("警告", "导入的物理量数量与UI创建的输入框数量不完全匹配。")
                            break

                messagebox.showinfo("导入成功", "配置已成功导入。")
            except Exception as e:
                messagebox.showerror("导入失败", f"无法导入配置文件: {e}")

    def export_config(self):
        """导出当前配置到文件"""
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
                        # 再次检查 Entry 是否存在，以防在操作过程中被销毁
                        if entries[1].winfo_exists() and entries[2].winfo_exists():
                            value = entries[1].get().strip()
                            uncertainty = entries[2].get().strip()
                            f.write(f"{value},{uncertainty}\n")
                        else:
                            messagebox.showwarning("警告", f"物理量 x{i+1} 的输入框已销毁，未导出。")

                messagebox.showinfo("导出成功", f"配置已成功导出到 {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("导出失败", f"无法导出配置文件: {e}")

    def _update_results(self, y_value, u_y, error_info):
        """在主线程中更新结果标签或显示错误消息"""
        if error_info:
            messagebox.showerror(error_info[0], error_info[1])
        else:
            # 调用新的格式化函数
            formatted_value, formatted_uncertainty = format_uncertainty_and_value(y_value, u_y)
            self.result_value_label.configure(text=f"输出测量值 (y): {formatted_value}")
            self.result_uncertainty_label.configure(text=f"输出不确定度 (uy): {formatted_uncertainty}")