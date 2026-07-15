from manim import *


class DailyTemperatures(Scene):
    """Visualizes the monotonic stack technique for LeetCode 739
    (Daily Temperatures): for each day, find how many days until a
    warmer temperature.
    """

    def construct(self):
        temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
        n = len(temperatures)

        title = Text("Daily Temperatures — Monotonic Stack", font_size=34)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        # --- Temperature array (top row) ---
        temp_cells = VGroup()
        for value in temperatures:
            square = Square(side_length=1.0)
            square.set_stroke(WHITE, 2)
            label = Text(str(value), font_size=32)
            label.move_to(square.get_center())
            temp_cells.add(VGroup(square, label))
        temp_cells.arrange(RIGHT, buff=0)
        temp_cells.next_to(title, DOWN, buff=0.7)

        index_labels = VGroup()
        for i, cell in enumerate(temp_cells):
            idx = Text(str(i), font_size=20, color=GRAY)
            idx.next_to(cell, UP, buff=0.1)
            index_labels.add(idx)

        self.play(
            LaggedStartMap(FadeIn, temp_cells, shift=UP, lag_ratio=0.1),
            FadeIn(index_labels),
        )
        self.wait(0.3)

        # --- Answer array (below temperatures) ---
        answer_values = ["·"] * n
        answer_cells = VGroup()
        for _ in range(n):
            square = Square(side_length=1.0)
            square.set_stroke(GRAY, 2)
            label = Text("·", font_size=32, color=GRAY)
            label.move_to(square.get_center())
            answer_cells.add(VGroup(square, label))
        answer_cells.arrange(RIGHT, buff=0)
        answer_cells.next_to(temp_cells, DOWN, buff=1.0)

        answer_tag = Text("answer", font_size=24, color=GRAY)
        answer_tag.next_to(answer_cells, LEFT, buff=0.4)

        self.play(FadeIn(answer_cells), FadeIn(answer_tag))
        self.wait(0.3)

        def make_answer_cell(value, color=GREEN):
            square = Square(side_length=1.0)
            square.set_stroke(color, 2)
            label = Text(str(value), font_size=32, color=color)
            label.move_to(square.get_center())
            return VGroup(square, label)

        # --- Stack visualization (bottom-right, grows upward) ---
        stack_tag = Text("stack (indices)", font_size=24, color=YELLOW)
        stack_anchor = RIGHT * 5.3 + DOWN * 2.8
        stack_tag.move_to(stack_anchor + DOWN * 0.5)
        self.play(FadeIn(stack_tag))

        def make_stack_square(i):
            square = Square(side_length=0.9)
            square.set_stroke(YELLOW, 2)
            label = Text(f"{i} ({temperatures[i]})", font_size=22, color=YELLOW)
            label.move_to(square.get_center())
            return VGroup(square, label)

        stack = []  # list of indices
        stack_group = VGroup()  # mobjects mirroring `stack`

        def layout_stack_group():
            stack_group.arrange(UP, buff=0.05)
            stack_group.move_to(stack_anchor, aligned_edge=DOWN)

        # Pointer/arrow over the current index.
        pointer = Triangle(color=BLUE, fill_color=BLUE, fill_opacity=1)
        pointer.scale(0.18)
        pointer.rotate(PI)
        pointer.next_to(temp_cells[0], UP, buff=0.4)
        pointer_label = Text("i", font_size=24, color=BLUE)
        pointer_label.next_to(pointer, UP, buff=0.1)
        self.play(FadeIn(pointer), FadeIn(pointer_label))

        status = Text("scanning...", font_size=28, color=YELLOW)
        status.next_to(answer_cells, DOWN, buff=0.8)
        self.play(FadeIn(status))

        for i in range(n):
            new_pointer_pos = temp_cells[i].get_top() + UP * 0.4
            self.play(
                pointer.animate.move_to(new_pointer_pos),
                pointer_label.animate.next_to(new_pointer_pos, UP, buff=0.1),
                run_time=0.4,
            )

            # Pop while current temp is warmer than the temp at stack top.
            while stack and temperatures[i] > temperatures[stack[-1]]:
                prev_index = stack[-1]
                new_status = Text(
                    f"temp[{i}]={temperatures[i]} > temp[{prev_index}]="
                    f"{temperatures[prev_index]}: pop {prev_index}",
                    font_size=26,
                    color=YELLOW,
                )
                new_status.move_to(status)
                self.play(Transform(status, new_status), run_time=0.4)

                popped_box = stack_group[-1]
                self.play(popped_box.animate.set_color(GREEN), run_time=0.2)
                self.play(FadeOut(popped_box, shift=RIGHT), run_time=0.3)
                stack_group.remove(popped_box)
                stack.pop()
                layout_stack_group()

                wait_days = i - prev_index
                new_answer_cell = make_answer_cell(wait_days)
                new_answer_cell.move_to(answer_cells[prev_index])
                self.play(Transform(answer_cells[prev_index], new_answer_cell), run_time=0.4)
                self.wait(0.2)

            if not (stack and temperatures[i] > temperatures[stack[-1]]):
                if stack:
                    new_status = Text(
                        f"temp[{i}]={temperatures[i]} <= temp[{stack[-1]}]="
                        f"{temperatures[stack[-1]]}: stop popping",
                        font_size=26,
                        color=GRAY,
                    )
                else:
                    new_status = Text(
                        f"stack empty: nothing to compare", font_size=26, color=GRAY
                    )
                new_status.move_to(status)
                self.play(Transform(status, new_status), run_time=0.3)

            # Push current index.
            square = make_stack_square(i)
            stack.append(i)
            stack_group.add(square)
            layout_stack_group()
            self.play(FadeIn(square, shift=DOWN * 0.3), run_time=0.35)
            self.wait(0.2)

        # Remaining indices in the stack never found a warmer day -> answer stays 0.
        new_status = Text(
            "remaining indices in stack keep answer = 0", font_size=26, color=GRAY
        )
        new_status.move_to(status)
        self.play(Transform(status, new_status))

        final_zero_anims = []
        for idx in stack:
            new_cell = make_answer_cell(0, color=GRAY)
            new_cell.move_to(answer_cells[idx])
            final_zero_anims.append(Transform(answer_cells[idx], new_cell))
        if final_zero_anims:
            self.play(*final_zero_anims)

        self.wait(1.5)
