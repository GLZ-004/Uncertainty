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
        self.configure(bg_color="#f0f0f0") 

        # 创建一个主框架来容纳所有内容
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.current_page = None # 用于跟踪当前显示的页面

        self.create_main_menu()

    def clear_frame(self):
        """清除当前框架中的所有组件"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_frame()
        self.current_page = None # 重置当前页面

        # 标题
        self.title_label = ctk.CTkLabel(self.main_frame, text="不确定度计算器", font=("Arial", 30, "bold"))
        self.title_label.pack(pady=40)

        # 功能1按钮
        self.single_quantity_button = ctk.CTkButton(
            self.main_frame,
            text="1. 单个物理量不确定度的计算与合成",
            command=self.show_single_quantity_calculator,
            font=("Arial", 18),
            height=60,
            width=300
        )
        self.single_quantity_button.pack(pady=20)

        # 功能2按钮
        self.propagation_button = ctk.CTkButton(
            self.main_frame,
            text="2. 不确定度的传递",
            command=self.show_uncertainty_propagation_calculator,
            font=("Arial", 18),
            height=60,
            width=300
        )
        self.propagation_button.pack(pady=20)

    def show_single_quantity_calculator(self):
        self.clear_frame()
        self.current_page = SingleQuantityCalculator(self.main_frame, self)
        self.current_page.pack(fill="both", expand=True)


    def show_uncertainty_propagation_calculator(self):
        self.clear_frame()
        self.current_page = UncertaintyPropagationCalculator(self.main_frame, self)
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

    app = UncertaintyCalculatorApp()
    app.mainloop()