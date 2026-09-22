from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex


# --- Core Game Logic Functions ---

def get_big_small(num):
    return "Big" if num >= 5 else "Small"


def predict_pattern_1(history):
    if len(history) < 4:
        return "No Prediction"

    p1 = history[-4]
    p3 = history[-2]
    steps = (p3 - p1) % 10
    predicted_num = (p3 + steps) % 10

    return get_big_small(predicted_num)


def predict_pattern_2(history, period_counts):
    if len(history) < 2:
        return "No Prediction"

    last_num = history[-1]
    lookback = min(20, len(history) - 1)

    for i in range(2, lookback + 1):
        idx = len(history) - i

        if period_counts[idx] % 2 == 0:
            if history[idx] == last_num:
                if idx + 1 < len(history):
                    next_num = history[idx + 1]
                    return get_big_small(next_num)

    return "No Prediction"


def predict_pattern_3(history):
    if len(history) < 3:
        return "No Prediction"

    if (
        (history[-2] == 3 and history[-1] == 3)
        or (history[-2] == 6 and history[-1] == 8)
        or (history[-2] == 6 and history[-1] == 1)
    ):
        return "No Prediction"

    trigger_nums = {6, 3, 1, 8}
    window = []

    for num in reversed(history):
        window.append(num)

        if num in trigger_nums and len(window) >= 3:
            break

    if len(window) < 3:
        return "No Prediction"

    elements_to_count = window.copy()

    if elements_to_count and elements_to_count[0] in trigger_nums:
        elements_to_count.pop(0)

    if elements_to_count and elements_to_count[-1] in trigger_nums:
        elements_to_count.pop()

    big_count = sum(1 for x in elements_to_count if x >= 5)
    small_count = sum(1 for x in elements_to_count if x < 5)

    if big_count == small_count:
        return "No Prediction"

    return "Big" if big_count > small_count else "Small"


def predict_pattern_4(history):
    if len(history) < 5:
        return "No Prediction"

    last_5 = [get_big_small(x) for x in history[-5:]]

    seq1 = ["Small", "Big", "Small", "Small", "Big"]
    seq2 = ["Big", "Small", "Big", "Big", "Small"]
    seq3 = ["Small", "Big", "Big", "Small", "Small"]
    seq4 = ["Big", "Small", "Small", "Big", "Big"]

    if last_5 == seq1 or last_5 == seq2:
        return "Big"

    elif last_5 == seq3 or last_5 == seq4:
        return "Small"

    return "No Prediction"


def predict_new_combo_rules(history):
    if len(history) < 2:
        return "No Prediction"

    small_combo = {0, 2, 4}
    big_combo = {5, 7, 9}

    if len(history) >= 3:
        n0 = history[-3]
        n1 = history[-2]
        n2 = history[-1]

        if n0 in small_combo and n1 in small_combo and n2 in small_combo:
            return "No Prediction"

        if n0 in big_combo and n1 in big_combo and n2 in big_combo:
            return "No Prediction"

    last_n1 = history[-2]
    last_n2 = history[-1]

    if last_n1 in small_combo and last_n2 in small_combo:
        return "Small"

    if last_n1 in big_combo and last_n2 in big_combo:
        return "Big"

    return "No Prediction"


def predict_sequence_rule(history):
    if len(history) < 2:
        return "No Prediction"

    n1 = history[-2]
    n2 = history[-1]

    if n1 == 1 and n2 == 2:
        return "Small"

    if n1 == 4 and n2 == 5:
        return "Big"

    if n1 == 3 and n2 == 4:
        return "Big"

    return "No Prediction"


def predict_missing_average_rule(history):
    if len(history) < 100:
        return "No Prediction"

    votes = []

    for num in range(10):

        current_missing = 0

        for x in reversed(history):
            if x == num:
                break

            current_missing += 1

        appearances = [
            i for i, x in enumerate(history)
            if x == num
        ]

        if len(appearances) < 2:
            continue

        intervals = []

        for i in range(1, len(appearances)):
            intervals.append(
                appearances[i] - appearances[i - 1] - 1
            )

        avg_missing = sum(intervals) / len(intervals)

        if abs(current_missing - avg_missing) < 0.5:

            if 0 <= num <= 4:
                votes.append("Small")

            elif 5 <= num <= 9:
                votes.append("Big")

    if not votes:
        return "No Prediction"

    if votes.count("Big") > votes.count("Small"):
        return "Big"

    return "Small"


def calculate_final_result(predictions):

    valid_votes = [
        v for v in predictions
        if v != "No Prediction"
    ]

    if not valid_votes:
        return "No Prediction"

    big_votes = valid_votes.count("Big")
    small_votes = valid_votes.count("Small")

    if big_votes > small_votes:
        return "Big"

    elif small_votes > big_votes:
        return "Small"

    else:
        return "Big and Small"


# --- Kivy App Interface ---

class WingoPredictorApp(App):

    def build(self):

        self.history = []
        self.period_counts = []

        main_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # Title
        title = Label(
            text="WINGO SMART PREDICTOR",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=40,
            color=get_color_from_hex("#FFC107")
        )

        main_layout.add_widget(title)

        # Status
        self.status_label = Label(
            text="మొదటి 20 పీరియడ్స్ హిస్టరీ ఫిల్ చేయండి (ఇంకా 20 ఉన్నాయి)",
            font_size="14sp",
            size_hint_y=None,
            height=30
        )

        main_layout.add_widget(self.status_label)

        # Final prediction
        self.final_label = Label(
            text="WAITING FOR DATA",
            font_size="26sp",
            bold=True,
            size_hint_y=None,
            height=60,
            color=get_color_from_hex("#2196F3")
        )

        main_layout.add_widget(self.final_label)

        # Statistics
        self.stats_label = Label(
            text=(
                "1. Alternative: -\n"
                "2. Even Period: -\n"
                "3. Density Combo: -\n"
                "4. Fixed Seq: -\n"
                "5. Combo Rule: -\n"
                "6. Sequence Rule: -\n"
                "7. Missing Avg Rule: -"
            ),
            font_size="13sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=160
        )

        self.stats_label.bind(
            size=self.stats_label.setter("text_size")
        )

        main_layout.add_widget(self.stats_label)

        # Number buttons
        grid = GridLayout(
            cols=5,
            spacing=10,
            size_hint_y=None,
            height=120
        )

        for i in range(10):

            if i >= 5:
                btn_bg = get_color_from_hex("#4CAF50")
            else:
                btn_bg = get_color_from_hex("#F44336")

            btn = Button(
                text=str(i),
                background_normal="",
                background_color=btn_bg,
                font_size="18sp",
                bold=True
            )

            btn.bind(on_press=self.on_num_click)

            grid.add_widget(btn)

        main_layout.add_widget(grid)

        # Reset button
        reset_btn = Button(
            text="RESET HISTORY",
            background_normal="",
            background_color=get_color_from_hex("#9C27B0"),
            font_size="16sp",
            size_hint_y=None,
            height=45
        )

        reset_btn.bind(on_press=self.reset_game)

        main_layout.add_widget(reset_btn)

        # History ScrollView
        scroll = ScrollView(
            size_hint=(1, None),
            height=80
        )

        self.history_label = Label(
            text="లైవ్ హిస్టరీ: ",
            font_size="12sp",
            size_hint_y=None,
            height=40,
            color=get_color_from_hex("#B0BEC5")
        )

        self.history_label.bind(
            size=self.history_label.setter("text_size")
        )

        scroll.add_widget(self.history_label)

        main_layout.add_widget(scroll)

        return main_layout


    def on_num_click(self, instance):

        num = int(instance.text)

        self.history.append(num)

        current_period = len(self.history)

        self.period_counts.append(current_period)

        # History display
        hist_str = ", ".join(
            [
                f"P{idx + 1}:{val}"
                for idx, val in enumerate(self.history)
            ]
        )

        self.history_label.text = (
            f"లైవ్ హిస్టరీ: {hist_str}"
        )

        self.history_label.height = max(
            80,
            self.history_label.texture_size[1] + 20
        )

        # First 20 periods
        if current_period < 20:

            self.status_label.text = (
                f"హిస్టరీ ఫిల్ అవుతోంది... "
                f"ఇంకా {20 - current_period} ఎంటర్ చేయాలి."
            )

            self.final_label.text = "WAITING FOR DATA"

            self.final_label.color = get_color_from_hex(
                "#2196F3"
            )

            return

        # After 20 periods
        self.status_label.text = (
            f"మొత్తం డేటా పీరియడ్స్: {current_period}"
        )

        p1 = predict_pattern_1(self.history)

        p2 = predict_pattern_2(
            self.history,
            self.period_counts
        )

        p3 = predict_pattern_3(self.history)

        p4 = predict_pattern_4(self.history)

        p5 = predict_new_combo_rules(self.history)

        p6 = predict_sequence_rule(self.history)

        p7 = predict_missing_average_rule(self.history)

        # Show individual predictions
        self.stats_label.text = (
            f"1. Alternative: {p1}\n"
            f"2. Even Period: {p2}\n"
            f"3. Density Combo: {p3}\n"
            f"4. Fixed Seq: {p4}\n"
            f"5. Combo Rule: {p5}\n"
            f"6. Sequence Rule: {p6}\n"
            f"7. Missing Avg Rule: {p7}"
        )

        # Final result
        all_predictions = [
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7
        ]

        final_decision = calculate_final_result(
            all_predictions
        )

        self.final_label.text = (
            f"PREDICTION: {final_decision}"
        )

        if final_decision == "Big":

            self.final_label.color = get_color_from_hex(
                "#4CAF50"
            )

        elif final_decision == "Small":

            self.final_label.color = get_color_from_hex(
                "#F44336"
            )

        else:

            self.final_label.color = get_color_from_hex(
                "#FFC107"
            )


    def reset_game(self, instance):

        self.history = []

        self.period_counts = []

        self.status_label.text = (
            "మొదటి 20 పీరియడ్స్ హిస్టరీ ఫిల్ చేయండి "
            "(ఇంకా 20 ఉన్నాయి)"
        )

        self.final_label.text = "WAITING FOR DATA"

        self.final_label.color = get_color_from_hex(
            "#2196F3"
        )

        self.stats_label.text = (
            "1. Alternative: -\n"
            "2. Even Period: -\n"
            "3. Density Combo: -\n"
            "4. Fixed Seq: -\n"
            "5. Combo Rule: -\n"
            "6. Sequence Rule: -\n"
            "7. Missing Avg Rule: -"
        )

        self.history_label.text = "లైవ్ హిస్టరీ: "
        self.history_label.height = 40


# --- Start Application ---

if __name__ == "__main__":
    WingoPredictorApp().run()