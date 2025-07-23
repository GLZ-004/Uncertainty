import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# 导入所有功能模块
from single_quantity import SingleQuantityCalculator
from uncertainty_propagation import UncertaintyPropagationCalculator

class UncertaintyCalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("不确定度计算器")
        self.geometry("900x700")
        # self.configure(fg_color="transparent") # 确保根窗口背景由主题控制

        # 配置根窗口的列和行权重，确保 main_frame 能够随窗口大小变化
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建一个主框架来容纳所有内容
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # 配置主框架的列和行权重，使其内部内容可以居中和伸缩
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1) # 顶部弹性空间
        self.main_frame.grid_rowconfigure(1, weight=0) # 标题行
        self.main_frame.grid_rowconfigure(2, weight=0) # 按钮1
        self.main_frame.grid_rowconfigure(3, weight=0) # 按钮2
        self.main_frame.grid_rowconfigure(4, weight=1) # 底部弹性空间


        self.current_page = None # 用于跟踪当前显示的页面

        self.create_main_menu()

    def clear_frame(self):
        """清除当前框架中的所有组件"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()
        self.current_page = None # 重置当前页面

        # 标题 - 进一步增大字号，强调应用名称
        self.title_label = ctk.CTkLabel(self.main_frame, text="不确定度计算器", font=("Arial", 42, "bold"))
        self.title_label.grid(row=1, column=0, pady=(80, 50), sticky="n") # 顶部更大留白，底部适中

        # 功能1按钮 - 更大的字体，按钮更宽更高
        self.single_quantity_button = ctk.CTkButton(
            self.main_frame,
            text="1. 单个物理量不确定度的计算与合成",
            command=self.show_single_quantity_calculator,
            font=("Arial", 22, "normal"), 
            height=70, # 按钮更高
            width=420, # 按钮更宽
            corner_radius=12 # 增加圆角
        )
        self.single_quantity_button.grid(row=2, column=0, pady=30) # 增加按钮间距

        # 功能2按钮 - 同上
        self.propagation_button = ctk.CTkButton(
            self.main_frame,
            text="2. 不确定度的传递",
            command=self.show_uncertainty_propagation_calculator,
            font=("Arial", 22, "normal"), 
            height=70, # 按钮更高
            width=420, # 按钮更宽
            corner_radius=12 # 增加圆角
        )
        self.propagation_button.grid(row=3, column=0, pady=30)

    def show_single_quantity_calculator(self):
        self.clear_frame()
        self.current_page = SingleQuantityCalculator(self.main_frame, self)
        self.current_page.grid(row=0, column=0, columnspan=1, rowspan=5, sticky="nsew")


    def show_uncertainty_propagation_calculator(self):
        self.clear_frame()
        self.current_page = UncertaintyPropagationCalculator(self.main_frame, self)
        self.current_page.grid(row=0, column=0, columnspan=1, rowspan=5, sticky="nsew")


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")  # Modes: "System" (default), "Dark", "Light" - 苹果风格偏向明亮
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

    app = UncertaintyCalculatorApp()
    app.mainloop()