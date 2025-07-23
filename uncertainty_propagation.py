import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from calculation_formulas import propagate_uncertainty, parse_float_list ,format_uncertainty_and_value
import os
import threading

# 如果要使用图片图标，请取消注释并确保图片文件存在
# from PIL import Image
# BACK_ICON_PATH = "icons/back_arrow.png"
# ADD_ICON_PATH = "icons/add.png"
# REMOVE_ICON_PATH = "icons/remove.png"
# IMPORT_ICON_PATH = "icons/import.png"
# EXPORT_ICON_PATH = "icons/export.png"
# INFO_ICON_PATH = "icons/info.png"

class UncertaintyPropagationCalculator(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent")
        self.app = app_instance

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0)
        self.grid_rowconfigure(7, weight=1)

        self.input_vars_count = 1
        self.input_var_entries = []
        
        self.info_tooltip_window = None # 用于存储提示窗口实例

        # 移除与鼠标悬浮相关的标志位和任务ID
        # self._tooltip_show_job = None
        # self._tooltip_hide_job = None
        # self._mouse_is_over_info_button = False 
        # self._mouse_is_over_tooltip_window = False

        self.create_widgets()

    def create_widgets(self):
        # ... (此部分保持不变，与您上一次提供的代码一致) ...
        self.title_label = ctk.CTkLabel(self, text="不确定度的传递", font=("Arial", 30, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(25, 15), sticky="n")

        self.back_button = ctk.CTkButton(
            self, 
            text="← 返回主菜单", 
            command=self.app.create_main_menu,
            width=120, 
            height=35, 
            font=("Arial", 15, "bold"),
            corner_radius=9,
            fg_color="transparent",
            text_color=("blue", "lightblue"),
            hover_color=("gray85", "gray20")
        )
        self.back_button.grid(row=0, column=1, padx=25, pady=(25, 15), sticky="ne")

        function_input_frame = ctk.CTkFrame(self, fg_color="transparent")
        function_input_frame.grid(row=1, column=0, columnspan=2, padx=30, pady=(15, 5), sticky="ew")
        function_input_frame.grid_columnconfigure(0, weight=0)
        function_input_frame.grid_columnconfigure(1, weight=1)
        function_input_frame.grid_columnconfigure(2, weight=0)

        self.function_label = ctk.CTkLabel(function_input_frame, text="函数关系 y = f(x1, x2, ...):", font=("Arial", 16, "bold"))
        self.function_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
        
        self.function_entry = ctk.CTkEntry(function_input_frame, placeholder_text="例如: x1*x2 + sin(x3)", height=35, font=("Arial", 16))
        self.function_entry.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="ew")

        self.info_button = ctk.CTkButton(
            function_input_frame,
            text="?",
            width=35,
            height=35,
            font=("Arial", 18, "bold"),
            corner_radius=10,
            fg_color=("gray80", "gray25"),
            text_color=("black", "white"),
            hover_color=("gray70", "gray35"),
            command=self.toggle_symbols_display # 关键改动：改为点击事件
        )
        self.info_button.grid(row=0, column=2, padx=0, pady=0, sticky="e")

        # 移除鼠标悬浮事件绑定
        # self.info_button.bind("<Enter>", self._on_info_button_enter)
        # self.info_button.bind("<Leave>", self._on_info_button_leave)
        
        # ... (以下部分保持不变) ...

        self.input_vars_frame = ctk.CTkScrollableFrame(
            self, 
            label_text="输入物理量 (x, ux)", 
            height=200, 
            corner_radius=12, 
            fg_color=("gray92", "gray10"),
            label_font=("Arial", 17, "bold")
        )
        self.input_vars_frame.grid(row=2, column=0, columnspan=2, padx=30, pady=15, sticky="nsew")
        self.input_vars_frame.grid_columnconfigure(0, weight=0)
        self.input_vars_frame.grid_columnconfigure(1, weight=1)
        self.input_vars_frame.grid_columnconfigure(2, weight=1)

        self.add_var_button = ctk.CTkButton(
            self, 
            text="＋ 添加物理量",
            command=self.add_input_variable,
            height=38,
            width=130,
            font=("Arial", 16, "bold"),
            corner_radius=9
        )
        self.add_var_button.grid(row=3, column=0, padx=30, pady=(10, 5), sticky="w")
        
        self.remove_var_button = ctk.CTkButton(
            self, 
            text="− 移除物理量",
            command=self.remove_input_variable,
            height=38,
            width=130,
            font=("Arial", 16, "bold"),
            corner_radius=9
        )
        self.remove_var_button.grid(row=3, column=1, padx=30, pady=(10, 5), sticky="e")

        self.render_input_variables()

        self.calculate_button = ctk.CTkButton(
            self, 
            text="计算传递不确定度", 
            command=self.perform_calculation_thread, 
            font=("Arial", 22, "normal"),
            height=55,
            width=280,
            corner_radius=12
        )
        self.calculate_button.grid(row=4, column=0, columnspan=2, pady=25)

        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=5, column=0, columnspan=2, padx=30, pady=(10, 20), sticky="ew")
        self.result_frame.grid_columnconfigure((0, 1), weight=1)

        self.result_value_label = ctk.CTkLabel(self.result_frame, text="输出测量值 (y): ", font=("Arial", 22, "bold"))
        self.result_value_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.result_uncertainty_label = ctk.CTkLabel(self.result_frame, text="输出不确定度 (uy): ", font=("Arial", 22, "bold"))
        self.result_uncertainty_label.grid(row=0, column=1, padx=15, pady=8, sticky="w")
        
        self.io_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.io_frame.grid(row=6, column=0, columnspan=2, padx=30, pady=(10, 10), sticky="ew")
        self.io_frame.grid_columnconfigure((0, 1), weight=1)

        self.import_button = ctk.CTkButton(
            self.io_frame, 
            text="⬇️ 导入配置",
            command=self.import_config,
            height=38,
            width=130,
            font=("Arial", 16, "bold"),
            corner_radius=9
        )
        self.import_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.export_button = ctk.CTkButton(
            self.io_frame, 
            text="⬆️ 导出配置",
            command=self.export_config,
            height=38,
            width=130,
            font=("Arial", 16, "bold"),
            corner_radius=9
        )
        self.export_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def get_common_symbols_text(self):
        # ... (此方法保持不变) ...
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

    # 新增的点击事件处理方法
    def toggle_symbols_display(self):
        """点击按钮时显示或隐藏提示窗口"""
        if self.info_tooltip_window and self.info_tooltip_window.winfo_exists():
            self._hide_tooltip_now() # 如果已显示，则隐藏
        else:
            self._show_tooltip_now() # 如果未显示，则显示

    # 原有的 _schedule_show_tooltip, _on_info_button_enter, _on_info_button_leave,
    # _on_tooltip_window_enter, _on_tooltip_window_leave, _schedule_hide_tooltip
    # 都将被移除或替换为更简单的 _show_tooltip_now/_hide_tooltip_now 调用。

    def _show_tooltip_now(self):
        """实际显示提示框的逻辑 (点击模式)"""
        if self.info_tooltip_window and self.info_tooltip_window.winfo_exists():
            return # 已经显示了，直接返回

        # 获取按钮的屏幕坐标和尺寸
        self.info_button.update_idletasks() # 确保获取最新的几何信息
        btn_x_root = self.info_button.winfo_rootx()
        btn_y_root = self.info_button.winfo_rooty()
        btn_width = self.info_button.winfo_width()
        # btn_height = self.info_button.winfo_height() # 在此模式下不直接需要，但可以保留

        # 创建 Toplevel 窗口
        self.info_tooltip_window = tk.Toplevel(self)
        self.info_tooltip_window.wm_overrideredirect(True) # 移除窗口边框和标题栏
        try:
            self.info_tooltip_window.wm_attributes("-alpha", 0.98) 
        except Exception:
            pass

        tooltip_frame = ctk.CTkFrame(
            self.info_tooltip_window,
            corner_radius=12,
            fg_color=("gray95", "gray15"),
            border_width=1,
            border_color=("gray70", "gray30")
        )
        tooltip_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tooltip_textbox = ctk.CTkTextbox(
            tooltip_frame,
            wrap="word",
            height=280,
            width=400,
            font=("Arial", 13),
            fg_color="transparent",
            activate_scrollbars=True
        )
        tooltip_textbox.insert("0.0", self.get_common_symbols_text())
        tooltip_textbox.configure(state="disabled")
        tooltip_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.info_tooltip_window.update_idletasks()
        tooltip_width = self.info_tooltip_window.winfo_width()
        tooltip_height = self.info_tooltip_window.winfo_height()

        # 计算提示框的最佳位置
        x_pos = btn_x_root + btn_width + 10 # 放在按钮右侧
        y_pos = btn_y_root + 5

        # 检查是否超出屏幕右边界
        screen_width = self.winfo_screenwidth()
        if x_pos + tooltip_width > screen_width - 20: # 留20px边距
            x_pos = btn_x_root - tooltip_width - 10 # 放在按钮左侧
            if x_pos < 10:
                x_pos = 10 

        # 检查是否超出屏幕下边界
        screen_height = self.winfo_screenheight()
        if y_pos + tooltip_height > screen_height - 20: # 留20px边距
            y_pos = btn_y_root - tooltip_height - 5 # 放在按钮上方
            if y_pos < 10:
                y_pos = 10 

        self.info_tooltip_window.wm_geometry(f"+{x_pos}+{y_pos}")

        # 在点击模式下，不再需要Toplevel本身的鼠标Enter/Leave事件
        # 因为它不再由鼠标悬浮控制自动隐藏，而是由按钮点击控制。
        # self.info_tooltip_window.bind("<Enter>", self._on_tooltip_window_enter)
        # self.info_tooltip_window.bind("<Leave>", self._on_tooltip_window_leave)

    def _hide_tooltip_now(self):
        """实际隐藏提示框的逻辑 (点击模式)"""
        if self.info_tooltip_window and self.info_tooltip_window.winfo_exists():
            self.info_tooltip_window.destroy()
            self.info_tooltip_window = None
        # 移除相关的任务ID，在点击模式下这些job不再使用
        # self._tooltip_show_job = None
        # self._tooltip_hide_job = None

    # 移除所有与鼠标悬浮相关的调度和管理方法：
    # _schedule_show_tooltip, _on_info_button_enter, _on_info_button_leave,
    # _on_tooltip_window_enter, _on_tooltip_window_leave, _schedule_hide_tooltip, _cancel_hide_tooltip

    def render_input_variables(self):
        # ... (此方法保持不变) ...
        for label, value_entry, uncertainty_entry in self.input_var_entries:
            label.destroy()
            value_entry.destroy()
            uncertainty_entry.destroy()
        self.input_var_entries.clear()

        for i in range(self.input_vars_count):
            row_num = i 
            
            var_name_label = ctk.CTkLabel(self.input_vars_frame, text=f"x{i+1}:", font=("Arial", 16, "bold"))
            var_name_label.grid(row=row_num, column=0, padx=(15, 5), pady=10, sticky="e")

            value_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"x{i+1} 测量值", width=160, height=32, font=("Arial", 15))
            value_entry.grid(row=row_num, column=1, padx=5, pady=10, sticky="ew")

            uncertainty_entry = ctk.CTkEntry(self.input_vars_frame, placeholder_text=f"ux{i+1} 不确定度", width=160, height=32, font=("Arial", 15))
            uncertainty_entry.grid(row=row_num, column=2, padx=(5, 15), pady=10, sticky="ew")
            
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
        # ... (此方法保持不变) ...
        self.calculate_button.configure(state="disabled", text="计算中...")
        self.import_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.add_var_button.configure(state="disabled")
        self.remove_var_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        
        thread = threading.Thread(target=self._perform_propagation_calculation_safe)
        thread.start()

    def _perform_propagation_calculation_safe(self):
        # ... (此方法保持不变) ...
        try:
            function_str = self.function_entry.get().strip()
            
            x_values_collected = {}
            u_x_values_collected = {}

            for i, entries in enumerate(self.input_var_entries):
                var_name = f"x{i+1}"
                
                if not entries[1].winfo_exists() or not entries[2].winfo_exists():
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

            y_value, u_y = propagate_uncertainty(function_str, x_values_collected, u_x_values_collected)

            self.app.after(10, self._update_results, y_value, u_y, None)

        except ValueError as e:
            self.app.after(10, self._update_results, None, None, ("输入错误", str(e)))
        except Exception as e:
            self.app.after(10, self._update_results, None, None, ("计算错误", f"发生未知错误: {e}"))
        finally:
            self.app.after(10, self._re_enable_buttons)

    def _update_results(self, y_value, u_y, error_info):
        # ... (此方法保持不变) ...
        if error_info:
            messagebox.showerror(error_info[0], error_info[1])
            self.result_value_label.configure(text=f"输出测量值 (y): ")
            self.result_uncertainty_label.configure(text=f"输出不确定度 (uy): ")
        else:
            formatted_value, formatted_uncertainty = format_uncertainty_and_value(y_value, u_y)
            self.result_value_label.configure(text=f"输出测量值 (y): {formatted_value}")
            self.result_uncertainty_label.configure(text=f"输出不确定度 (uy): {formatted_uncertainty}")

    def _re_enable_buttons(self):
        # ... (此方法保持不变) ...
        self.calculate_button.configure(state="normal", text="计算传递不确定度")
        self.import_button.configure(state="normal")
        self.export_button.configure(state="normal")
        self.add_var_button.configure(state="normal")
        self.remove_var_button.configure(state="normal")
        self.back_button.configure(state="normal")


    def import_config(self):
        # ... (此方法保持不变) ...
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
                    
                    self.function_entry.delete(0, ctk.END)
                    self.function_entry.insert(0, lines[0].strip())

                    input_data = []
                    for line in lines[1:]:
                        parts = [p.strip() for p in line.strip().split(',')]
                        if len(parts) == 2:
                            input_data.append((parts[0], parts[1]))
                        else:
                            raise ValueError(f"物理量行格式不正确: {line.strip()}。应为 '值,不确定度'。")
                    
                    self.input_vars_count = len(input_data)
                    self.render_input_variables()

                    for i, (value_str, uncertainty_str) in enumerate(input_data):
                        if i < len(self.input_var_entries):
                            self.input_var_entries[i][1].delete(0, ctk.END)
                            self.input_var_entries[i][1].insert(0, value_str)
                            self.input_var_entries[i][2].delete(0, ctk.END)
                            self.input_var_entries[i][2].insert(0, uncertainty_str)
                        else:
                            messagebox.showwarning("警告", "导入的物理量数量与UI创建的输入框数量不完全匹配。")
                            break

                messagebox.showinfo("导入成功", "配置已成功导入。")
            except Exception as e:
                messagebox.showerror("导入失败", f"无法导入配置文件: {e}")

    def export_config(self):
        # ... (此方法保持不变) ...
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.function_entry.get().strip() + "\n")
                    
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