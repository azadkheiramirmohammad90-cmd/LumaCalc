
import ast
import math
import operator
import random

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner


# ---------- Safe calculator engine ----------

def fact(x):
    if x < 0 or int(x) != x or x > 170:
        raise ValueError("Invalid factorial")
    return math.factorial(int(x))


def cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def round_num(x):
    return round(x)


FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "sqrt": math.sqrt, "cbrt": cbrt,
    "log": math.log10, "ln": math.log,
    "abs": abs, "floor": math.floor, "ceil": math.ceil,
    "round": round_num, "fact": fact,
    "exp": math.exp,
}

CONSTANTS = {"pi": math.pi, "e": math.e}

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_eval(expression):
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")
    expression = expression.replace("^", "**")
    expression = expression.replace("π", "pi")
    expression = expression.replace("√", "sqrt")

    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid value")

        if isinstance(node, ast.Name):
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError("Unknown name")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in BIN_OPS:
                raise ValueError("Invalid operator")

            left = visit(node.left)
            right = visit(node.right)

            if op_type is ast.Pow and abs(right) > 1000:
                raise ValueError("Power too large")

            result = BIN_OPS[op_type](left, right)
            if abs(result) > 1e100:
                raise ValueError("Result too large")
            return result

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in UNARY_OPS:
                raise ValueError("Invalid unary operator")
            return UNARY_OPS[op_type](visit(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function")
            name = node.func.id
            if name not in FUNCTIONS or node.keywords:
                raise ValueError("Unknown function")
            args = [visit(arg) for arg in node.args]
            return FUNCTIONS[name](*args)

        raise ValueError("Invalid expression")

    result = visit(tree)

    if isinstance(result, complex):
        raise ValueError("Complex result")
    if not math.isfinite(result):
        raise ValueError("Invalid result")
    return result


# ---------- 36 themes ----------

PALETTES = [
    ((0.93, 0.97, 1, 1), (0.80, 0.89, 1, 1), (0.25, 0.35, 0.65, 1)),
    ((0.08, 0.10, 0.16, 1), (0.17, 0.20, 0.29, 1), (0.35, 0.75, 1, 1)),
    ((0.96, 0.94, 0.89, 1), (0.88, 0.82, 0.72, 1), (0.40, 0.28, 0.20, 1)),
    ((0.91, 0.97, 0.92, 1), (0.72, 0.88, 0.77, 1), (0.12, 0.42, 0.29, 1)),
    ((0.98, 0.92, 0.96, 1), (0.91, 0.76, 0.87, 1), (0.55, 0.23, 0.48, 1)),
    ((0.94, 0.94, 0.99, 1), (0.80, 0.80, 0.93, 1), (0.32, 0.29, 0.59, 1)),
]


class LumaCalc(App):
    def build(self):
        self.memory = 0
        self.degrees = True
        self.scientific_open = False
        self.theme_index = 0
        self.expression = "0"

        self.apply_theme()

        self.root_box = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        self.title = Label(
            text="LumaCalc ✨",
            font_size=dp(26),
            bold=True,
            color=self.accent,
            size_hint_y=None,
            height=dp(42)
        )
        self.root_box.add_widget(self.title)

        top = BoxLayout(
            size_hint_y=None,
            height=dp(42),
            spacing=dp(6)
        )

        self.theme_spinner = Spinner(
            text="Theme 1/36",
            values=tuple(f"Theme {i}/36" for i in range(1, 37)),
            size_hint_x=0.55
        )
        self.theme_spinner.bind(text=self.change_theme)
        top.add_widget(self.theme_spinner)

        self.angle_button = Button(
            text="DEG",
            size_hint_x=0.45
        )
        self.angle_button.bind(on_press=self.toggle_angle)
        top.add_widget(self.angle_button)
        self.root_box.add_widget(top)

        self.display = TextInput(
            text="0",
            multiline=False,
            readonly=True,
            halign="right",
            font_size=dp(34),
            size_hint_y=None,
            height=dp(85),
            background_color=self.bg,
            foreground_color=self.accent,
            cursor_color=self.accent,
            padding=[dp(8), dp(15)]
        )
        self.root_box.add_widget(self.display)

        self.science_button = Button(
            text="Scientific functions  ▼",
            size_hint_y=None,
            height=dp(42)
        )
        self.science_button.bind(on_press=self.toggle_scientific)
        self.root_box.add_widget(self.science_button)

        self.science_grid = GridLayout(
            cols=4,
            spacing=dp(5),
            size_hint_y=None
        )
        self.science_grid.bind(
            minimum_height=self.science_grid.setter("height")
        )

        scientific = [
            "sin", "cos", "tan", "asin",
            "acos", "atan", "sinh", "cosh",
            "tanh", "√", "cbrt", "x²",
            "x³", "xʸ", "10ˣ", "eˣ",
            "log", "ln", "1/x", "|x|",
            "n!", "floor", "ceil", "round",
            "mod", "π", "e", "abs"
        ]

        for text in scientific:
            self.science_grid.add_widget(
                self.make_button(text, height=42)
            )

        self.science_scroll = ScrollView(
            size_hint_y=None,
            height=dp(0),
            do_scroll_x=False
        )
        self.science_scroll.add_widget(self.science_grid)
        self.root_box.add_widget(self.science_scroll)

        basic_scroll = ScrollView(do_scroll_x=False)

        self.basic_grid = GridLayout(
            cols=4,
            spacing=dp(5),
            size_hint_y=None
        )
        self.basic_grid.bind(
            minimum_height=self.basic_grid.setter("height")
        )

        buttons = [
            "MC", "MR", "M+", "M-",
            "C", "⌫", "(", ")",
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "−",
            "0", ".", "%", "+",
            "±", "AC", "=", " "
        ]

        for text in buttons:
            self.basic_grid.add_widget(
                self.make_button(text, height=52)
            )

        basic_scroll.add_widget(self.basic_grid)
        self.root_box.add_widget(basic_scroll)

        return self.root_box

    def apply_theme(self):
        self.bg, self.key_color, self.accent = (
            PALETTES[self.theme_index % len(PALETTES)]
        )
        Window.clearcolor = self.bg

    def change_theme(self, spinner, text):
        try:
            self.theme_index = int(text.split()[1].split("/")[0]) - 1
            self.apply_theme()
            self.refresh_colors()
        except (ValueError, IndexError):
            pass

    def refresh_colors(self):
        self.title.color = self.accent
        self.display.background_color = self.bg
        self.display.foreground_color = self.accent

        for grid in (self.basic_grid, self.science_grid):
            for button in grid.children:
                button.background_normal = ""
                button.background_color = self.key_color
                button.color = self.accent

    def make_button(self, text, height=48):
        button = Button(
            text=text,
            font_size=dp(17),
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_color=self.key_color,
            color=self.accent
        )

        if text in ("=",):
            button.background_color = (0.15, 0.55, 0.95, 1)
            button.color = (1, 1, 1, 1)
        elif text in ("C", "AC"):
            button.background_color = (0.9, 0.38, 0.42, 1)
            button.color = (1, 1, 1, 1)
        elif text in ("MC", "MR", "M+", "M-"):
            button.background_color = (0.45, 0.72, 0.48, 1)
            button.color = (1, 1, 1, 1)

        button.bind(on_press=self.button_pressed)
        return button

    def toggle_angle(self, instance):
        self.degrees = not self.degrees
        instance.text = "DEG" if self.degrees else "RAD"

    def toggle_scientific(self, instance):
        self.scientific_open = not self.scientific_open

        if self.scientific_open:
            self.science_scroll.height = dp(190)
            instance.text = "Scientific functions  ▲"
        else:
            self.science_scroll.height = dp(0)
            instance.text = "Scientific functions  ▼"

    def current_value(self):
        return safe_eval(self.display.text)

    def show_result(self, value):
        if isinstance(value, float) and value.is_integer():
            value = int(value)

        self.display.text = str(value)

    def append(self, value):
        if self.display.text in ("0", "Error", "تقسیم بر صفر"):
            self.display.text = value
        else:
            self.display.text += value

    def calculate(self):
        expression = self.display.text
        expression = expression.replace("%", "/100")
        self.show_result(safe_eval(expression))

    def apply_function(self, name):
        value = self.current_value()

        if name in ("sin", "cos", "tan"):
            if self.degrees:
                value = math.radians(value)
            result = FUNCTIONS[name](value)

        elif name in ("asin", "acos", "atan"):
            result = FUNCTIONS[name](value)
            if self.degrees:
                result = math.degrees(result)

        elif name == "sqrt":
            result = math.sqrt(value)
        elif name == "cbrt":
            result = cbrt(value)
        elif name == "square":
            result = value ** 2
        elif name == "cube":
            result = value ** 3
        elif name == "power":
            self.append("^")
            return
        elif name == "ten":
            result = 10 ** value
        elif name == "exp":
            result = math.exp(value)
        elif name == "reciprocal":
            result = 1 / value
        elif name == "factorial":
            result = fact(value)
        elif name == "mod":
            self.append("%")
            return
        elif name == "pi":
            self.append("π")
            return
        elif name == "e":
            self.append("e")
            return
        else:
            result = FUNCTIONS[name](value)

        self.show_result(result)

    def button_pressed(self, instance):
        value = instance.text

        try:
            if value in ("C", "AC"):
                self.display.text = "0"

            elif value == "⌫":
                self.display.text = (
                    self.display.text[:-1]
                    if len(self.display.text) > 1 else "0"
                )

            elif value == "MC":
                self.memory = 0

            elif value == "MR":
                self.show_result(self.memory)

            elif value == "M+":
                self.memory += self.current_value()

            elif value == "M-":
                self.memory -= self.current_value()

            elif value == "=":
                self.calculate()

            elif value == "±":
                self.show_result(-self.current_value())

            elif value in ("sin", "cos", "tan", "asin",
                           "acos", "atan", "sinh", "cosh",
                           "tanh", "√", "cbrt", "x²", "x³",
                           "xʸ", "10ˣ", "eˣ", "log", "ln",
                           "1/x", "|x|", "n!", "floor", "ceil",
                           "round", "mod", "π", "e", "abs"):

                names = {
                    "√": "sqrt", "x²": "square", "x³": "cube",
                    "xʸ": "power", "10ˣ": "ten", "eˣ": "exp",
                    "1/x": "reciprocal", "n!": "factorial",
                    "|x|": "abs", "π": "pi"
                }

                name = names.get(value, value)
                self.apply_function(name)

            elif value == " ":
                pass

            else:
                self.append(value)

        except ZeroDivisionError:
            self.display.text = "تقسیم بر صفر"
        except Exception:
            self.display.text = "Error"


if __name__ == "__main__":
    LumaCalc().run()
