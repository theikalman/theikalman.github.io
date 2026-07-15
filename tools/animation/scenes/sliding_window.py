from manim import *


class SlidingWindow(Scene):
    """Visualizes the sliding window technique: finding the maximum sum
    of any contiguous subarray of size `k` in an array of numbers.
    """

    def construct(self):
        values = [2, 1, 5, 1, 3, 2, 7, 4]
        k = 3

        # Build the array as a row of squares with numbers inside.
        cells = VGroup()
        for value in values:
            square = Square(side_length=1.0)
            square.set_stroke(WHITE, 2)
            label = Text(str(value), font_size=36)
            label.move_to(square.get_center())
            cell = VGroup(square, label)
            cells.add(cell)
        cells.arrange(RIGHT, buff=0)
        cells.to_edge(UP, buff=1.5)

        self.play(LaggedStartMap(FadeIn, cells, shift=UP, lag_ratio=0.1))
        self.wait(0.5)

        # Window highlight rectangle covering the first `k` cells.
        window = SurroundingRectangle(
            VGroup(*cells[:k]), color=YELLOW, buff=0.05, stroke_width=5
        )

        sum_label = Text("Window sum:", font_size=32)
        sum_value = Text(str(sum(values[:k])), font_size=32, color=YELLOW)
        sum_group = VGroup(sum_label, sum_value).arrange(RIGHT, buff=0.3)
        sum_group.next_to(cells, DOWN, buff=1.2)

        best_label = Text("Max sum:", font_size=32)
        best_value = Text(str(sum(values[:k])), font_size=32, color=GREEN)
        best_group = VGroup(best_label, best_value).arrange(RIGHT, buff=0.3)
        best_group.next_to(sum_group, DOWN, buff=0.5)

        self.play(Create(window), Write(sum_group), Write(best_group))
        self.wait(0.5)

        best_sum = sum(values[:k])

        for start in range(1, len(values) - k + 1):
            current_sum = sum(values[start : start + k])
            best_sum = max(best_sum, current_sum)

            new_window = SurroundingRectangle(
                VGroup(*cells[start : start + k]),
                color=YELLOW,
                buff=0.05,
                stroke_width=5,
            )
            new_sum_value = Text(str(current_sum), font_size=32, color=YELLOW)
            new_sum_value.move_to(sum_value, aligned_edge=LEFT)

            new_best_value = Text(str(best_sum), font_size=32, color=GREEN)
            new_best_value.move_to(best_value, aligned_edge=LEFT)

            self.play(
                Transform(window, new_window),
                Transform(sum_value, new_sum_value),
                Transform(best_value, new_best_value),
                run_time=0.7,
            )
            self.wait(0.3)

        self.wait(1)
