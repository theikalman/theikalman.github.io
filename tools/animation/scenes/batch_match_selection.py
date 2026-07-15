from manim import *


class BatchMatchSelection(Scene):
    """Visualizes Engine.FormMatches / selectBestWindow: claim a batch of
    tickets across the full MMR range, sort by MMR, then repeatedly slide a
    variable-size window to find the group of 2..max_players with the
    smallest MMR spread, forming a match and recursing on the remainder.
    """

    def construct(self):
        mmrs = [1620, 1480, 1510, 1750, 1495, 1690, 1505, 1640, 1500, 1660]
        max_players = 4

        title = Text("Batch-Claim + Tightest-Spread Selection", font_size=34)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        def make_cell(value, color=WHITE):
            square = Square(side_length=1.1)
            square.set_stroke(color, 2)
            label = Text(str(value), font_size=28, color=color)
            label.move_to(square.get_center())
            return VGroup(square, label)

        cells = VGroup(*[make_cell(v) for v in mmrs])
        cells.arrange(RIGHT, buff=0.15)
        cells.next_to(title, DOWN, buff=0.9)

        unsorted_tag = Text("claimed batch (unsorted)", font_size=24, color=GRAY)
        unsorted_tag.next_to(cells, UP, buff=0.2)

        self.play(
            LaggedStartMap(FadeIn, cells, shift=UP, lag_ratio=0.08),
            FadeIn(unsorted_tag),
        )
        self.wait(0.5)

        # --- Sort by MMR ---
        status = Text("sort candidates by MMR", font_size=28, color=YELLOW)
        status.next_to(cells, DOWN, buff=1.0)
        self.play(FadeIn(status))

        order = sorted(range(len(mmrs)), key=lambda i: mmrs[i])
        sorted_positions = [cells[i].get_center() for i in range(len(mmrs))]
        anims = []
        for new_pos, orig_idx in zip(sorted_positions, order):
            anims.append(cells[orig_idx].animate.move_to(new_pos))
        self.play(*anims, run_time=1.2)
        self.play(FadeOut(unsorted_tag))
        self.wait(0.3)

        sorted_cells = VGroup(*[cells[i] for i in order])
        sorted_values = [mmrs[i] for i in order]

        new_status = Text("scan for tightest-spread window", font_size=28, color=YELLOW)
        new_status.move_to(status)
        self.play(FadeOut(status))
        self.play(FadeIn(new_status))
        status = new_status
        self.wait(0.3)

        remaining_cells = list(sorted_cells)
        remaining_values = list(sorted_values)
        match_count = 0

        while len(remaining_values) >= 2:
            n = len(remaining_values)
            k_max = min(max_players, n)

            best_spread = None
            best_start, best_k = 0, min(2, n)

            window = None
            spread_caption = Text("scanning windows...", font_size=26, color=BLUE)
            spread_caption.next_to(status, DOWN, buff=0.5)
            self.play(FadeIn(spread_caption))

            for k in range(2, k_max + 1):
                for start in range(0, n - k + 1):
                    group = remaining_values[start : start + k]
                    spread = group[-1] - group[0]

                    group_cells = VGroup(*remaining_cells[start : start + k])
                    new_window = SurroundingRectangle(
                        group_cells, color=BLUE, buff=0.08, stroke_width=4
                    )
                    new_caption = Text(
                        f"size {k}, spread {spread}", font_size=26, color=BLUE
                    )
                    new_caption.move_to(spread_caption)

                    # Text mobjects with different content morph glyph-by-glyph
                    # under Transform, which reads as garbled overlap. A
                    # simultaneous FadeOut/FadeIn still cross-fades the two
                    # captions on top of each other, so fade the old caption
                    # out completely before fading the new one in.
                    if window is None:
                        window = new_window
                        self.play(Create(window), FadeOut(spread_caption), run_time=0.15)
                    else:
                        self.play(
                            Transform(window, new_window),
                            FadeOut(spread_caption),
                            run_time=0.12,
                        )
                    self.play(FadeIn(new_caption), run_time=0.12)
                    spread_caption = new_caption

                    if best_spread is None or spread < best_spread:
                        best_spread = spread
                        best_start, best_k = start, k

            best_group_cells = VGroup(
                *remaining_cells[best_start : best_start + best_k]
            )
            best_window = SurroundingRectangle(
                best_group_cells, color=GREEN, buff=0.08, stroke_width=5
            )
            match_status = Text(
                f"tightest window: size {best_k}, spread {best_spread} -> form match",
                font_size=26,
                color=GREEN,
            )
            match_status.move_to(spread_caption)
            self.play(
                Transform(window, best_window),
                FadeOut(spread_caption),
                run_time=0.25,
            )
            self.play(FadeIn(match_status), run_time=0.25)
            spread_caption = match_status
            self.wait(0.4)

            for c in remaining_cells[best_start : best_start + best_k]:
                c.generate_target()
                c[0].set_stroke(GREEN)
                c[1].set_color(GREEN)
            self.play(
                *[
                    c.animate.set_color(GREEN)
                    for c in remaining_cells[best_start : best_start + best_k]
                ],
                run_time=0.3,
            )
            self.play(
                FadeOut(best_group_cells, shift=DOWN * 0.5),
                FadeOut(window),
                FadeOut(spread_caption),
                run_time=0.5,
            )

            match_count += 1

            del remaining_cells[best_start : best_start + best_k]
            del remaining_values[best_start : best_start + best_k]

            if remaining_cells:
                self.play(
                    VGroup(*remaining_cells).animate.arrange(RIGHT, buff=0.15).move_to(
                        cells
                    ),
                    run_time=0.6,
                )
            self.wait(0.2)

        final_status = Text(
            f"{match_count} matches formed from a batch of {len(mmrs)} tickets",
            font_size=30,
            color=GREEN,
        )
        final_status.move_to(status)
        self.play(FadeOut(status))
        self.play(FadeIn(final_status))
        self.wait(1.5)
