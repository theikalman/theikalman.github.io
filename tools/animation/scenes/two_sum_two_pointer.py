from manim import *


class TwoSumTwoPointer(Scene):
    """Visualizes the two-pointer technique for finding a pair of numbers
    in a sorted array that add up to a given target.
    """

    def construct(self):
        values = [2, 4, 6, 8, 10, 12, 15]
        target = 18

        # Title / target display.
        title = Text("Two Sum (sorted array)", font_size=36)
        title.to_edge(UP, buff=0.6)

        target_label = Text("Target:", font_size=30)
        target_value = Text(str(target), font_size=30, color=YELLOW)
        target_group = VGroup(target_label, target_value).arrange(RIGHT, buff=0.3)
        target_group.next_to(title, DOWN, buff=0.4)

        self.play(Write(title), Write(target_group))

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
        cells.next_to(target_group, DOWN, buff=1.0)

        self.play(LaggedStartMap(FadeIn, cells, shift=UP, lag_ratio=0.1))
        self.wait(0.5)

        # Pointer markers (triangles) with L / R labels underneath each cell.
        def make_pointer(index, text, color):
            triangle = Triangle(color=color, fill_color=color, fill_opacity=1)
            triangle.scale(0.18)
            triangle.rotate(PI)
            triangle.next_to(cells[index], UP, buff=0.1)
            label = Text(text, font_size=28, color=color)
            label.next_to(triangle, UP, buff=0.1)
            return VGroup(triangle, label)

        left = 0
        right = len(values) - 1

        left_pointer = make_pointer(left, "L", BLUE)
        right_pointer = make_pointer(right, "R", RED)

        left_box = SurroundingRectangle(cells[left], color=BLUE, buff=0.05, stroke_width=5)
        right_box = SurroundingRectangle(cells[right], color=RED, buff=0.05, stroke_width=5)

        self.play(
            FadeIn(left_pointer),
            FadeIn(right_pointer),
            Create(left_box),
            Create(right_box),
        )
        self.wait(0.5)

        # Sum / status display.
        sum_text = Text(
            f"{values[left]} + {values[right]} = {values[left] + values[right]}",
            font_size=32,
        )
        sum_text.next_to(cells, DOWN, buff=1.0)

        status_text = Text("", font_size=30, color=GREEN)
        status_text.next_to(sum_text, DOWN, buff=0.4)

        self.play(Write(sum_text))
        self.wait(0.3)

        found = False
        while left < right and not found:
            current_sum = values[left] + values[right]

            new_sum_text = Text(
                f"{values[left]} + {values[right]} = {current_sum}", font_size=32
            )
            new_sum_text.move_to(sum_text)

            if current_sum == target:
                new_status = Text(
                    f"{current_sum} == {target}: found pair!", font_size=30, color=GREEN
                )
            elif current_sum < target:
                new_status = Text(
                    f"{current_sum} < {target}: move L right", font_size=30, color=BLUE
                )
            else:
                new_status = Text(
                    f"{current_sum} > {target}: move R left", font_size=30, color=RED
                )
            new_status.next_to(sum_text, DOWN, buff=0.4)

            self.play(
                Transform(sum_text, new_sum_text),
                Transform(status_text, new_status),
            )
            self.wait(0.5)

            if current_sum == target:
                found = True
                self.play(
                    left_box.animate.set_color(GREEN),
                    right_box.animate.set_color(GREEN),
                )
                self.wait(0.3)
                break

            if current_sum < target:
                left += 1
                new_left_box = SurroundingRectangle(
                    cells[left], color=BLUE, buff=0.05, stroke_width=5
                )
                new_left_pointer = make_pointer(left, "L", BLUE)
                self.play(
                    Transform(left_box, new_left_box),
                    Transform(left_pointer, new_left_pointer),
                    run_time=0.6,
                )
            else:
                right -= 1
                new_right_box = SurroundingRectangle(
                    cells[right], color=RED, buff=0.05, stroke_width=5
                )
                new_right_pointer = make_pointer(right, "R", RED)
                self.play(
                    Transform(right_box, new_right_box),
                    Transform(right_pointer, new_right_pointer),
                    run_time=0.6,
                )

            self.wait(0.3)

        self.wait(1.5)
