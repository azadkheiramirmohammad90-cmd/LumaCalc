import math

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.metrics import dp


class LumaCalc(App):

    def build(self):
        # رنگ پس‌زمینه
        Window.clearcolor = (0.93, 0.97, 1, 1)

        self.memory = 0

        main = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        # نام برنامه
        title = Label(
            text="LumaCalc ✨",
            font_size=dp(25),
            color=(0.25, 0.35, 0.65, 1),
            size_hint_y=0.08
        )
        main.add_widget(title)

        # صفحه نمایش
        self.display = Label(
            text="0",
            font_size=dp(38),
            color=(0.10, 0.15, 0.25, 1),
            halign="right",
            valign="middle",
            size_hint_y=0.18
        )

        self.display.bind(size=self.update_text_size)
        main.add_widget(self.display)

        # دکمه‌های ماشین حساب
        buttons = [
            ["MC", "MR", "M+", "M-"],
            ["sin", "cos", "tan", "√"],
            ["log", "ln", "π", "e"],
            ["(", ")", "^", "%"],
            ["C", "⌫", "÷", "×"],
            ["7", "8", "9", "−"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "="],
            ["0", ".", "", ""]
        ]

        grid = GridLayout(
            cols=4,
            spacing=dp(6),
            size_hint_y=0.74
        )

        for row in buttons:
            for text in row:

                if text == "":
                    grid.add_widget(Label())
                    continue

                button = Button(
                    text=text,
                    font_size=dp(22),
                    color=(0.12, 0.17, 0.28, 1),
                    background_normal="",
                    background_color=(0.80, 0.89, 1, 1)
                )

                # رنگ دکمه‌ها
                if text in ["MC", "MR", "M+", "M-"]:
                    button.background_color = (0.82, 0.90, 0.78, 1)

                elif text in ["sin", "cos", "tan", "√", "log", "ln"]:
                    button.background_color = (0.82, 0.80, 1, 1)

                elif text in ["π", "e", "^", "%"]:
                    button.background_color = (1.00, 0.84, 0.65, 1)

                elif text == "C":
                    button.background_color = (1.00, 0.65, 0.68, 1)

                elif text == "⌫":
                    button.background_color = (1.00, 0.78, 0.60, 1)

                elif text in ["÷", "×", "−", "+"]:
                    button.background_color = (0.70, 0.84, 1.00, 1)

                elif text == "=":
                    button.background_color = (0.35, 0.70, 1.00, 1)
                    button.color = (1, 1, 1, 1)

                button.bind(on_press=self.button_pressed)
                grid.add_widget(button)

        main.add_widget(grid)

        return main

    def update_text_size(self, instance, value):
        instance.text_size = instance.size

    def button_pressed(self, instance):
        value = instance.text

        # پاک کردن کامل
        if value == "C":
            self.display.text = "0"

        # حذف یک کاراکتر
        elif value == "⌫":
            if len(self.display.text) > 1:
                self.display.text = self.display.text[:-1]
            else:
                self.display.text = "0"

        # حافظه پاک
        elif value == "MC":
            self.memory = 0

        # حافظه خواندن
        elif value == "MR":
            self.display.text = str(self.memory)

        # اضافه کردن به حافظه
        elif value == "M+":
            try:
                self.memory += self.calculate_expression()
            except:
                pass

        # کم کردن از حافظه
        elif value == "M-":
            try:
                self.memory -= self.calculate_expression()
            except:
                pass

        # مساوی
        elif value == "=":
            self.calculate()

        # توابع ریاضی
        elif value == "sin":
            self.apply_function(math.sin)

        elif value == "cos":
            self.apply_function(math.cos)

        elif value == "tan":
            self.apply_function(math.tan)

        elif value == "√":
            self.apply_function(math.sqrt)

        elif value == "log":
            self.apply_function(math.log10)

        elif value == "ln":
            self.apply_function(math.log)

        # عدد پی
        elif value == "π":
            self.add_value("π")

        # عدد e
        elif value == "e":
            self.add_value("e")

        # توان
        elif value == "^":
            self.add_value("^")

        # درصد
        elif value == "%":
            try:
                result = self.calculate_expression() / 100
                self.display.text = str(result)
            except:
                self.display.text = "Error"

        else:
            self.add_value(value)

    def add_value(self, value):
        if self.display.text == "0":
            self.display.text = value
        else:
            self.display.text += value

    def prepare_expression(self):
        expression = self.display.text

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("^", "**")
        expression = expression.replace("π", "math.pi")
        expression = expression.replace("e", "math.e")

        return expression

    def calculate_expression(self):
        expression = self.prepare_expression()

        allowed = set(
            "0123456789+-*/(). "
        )

        # اجازه استفاده از math.pi و math.e
        if not all(
            char in allowed or char.isalpha()
            for char in expression
        ):
            raise ValueError()

        result = eval(
            expression,
            {
                "__builtins__": {},
                "math": math
            },
            {}
        )

        return result

    def calculate(self):
        try:
            result = self.calculate_expression()

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.display.text = str(result)

        except ZeroDivisionError:
            self.display.text = "تقسیم بر صفر"

        except:
            self.display.text = "Error"

    def apply_function(self, function):
        try:
            number = self.calculate_expression()
            result = function(number)

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.display.text = str(result)

        except:
            self.display.text = "Error"


LumaCalc().run()