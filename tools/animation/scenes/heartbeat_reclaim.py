from manim import *


class HeartbeatReclaim(Scene):
    """Visualizes the heartbeat/TTL/supervisor fault-tolerance mechanism:
    a worker refreshes its lock TTLs every heartbeat, crashes, the TTL bars
    count down to zero, and the supervisor's periodic scan detects the
    expired lease and reclaims the stranded tickets back to the queue.
    """

    def construct(self):
        title = Text("Heartbeat Lease + Supervisor Reclaim", font_size=34)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        worker_label = Text("Worker A", font_size=28, color=BLUE)
        worker_label.to_edge(LEFT, buff=0.8).shift(UP * 1.6)
        self.play(FadeIn(worker_label))

        # --- Claimed tickets with TTL bars ---
        def make_ticket(name):
            box = Square(side_length=0.9)
            box.set_stroke(BLUE, 2)
            label = Text(name, font_size=22, color=BLUE)
            label.move_to(box.get_center())
            bar_bg = Rectangle(width=0.9, height=0.15, stroke_width=1)
            bar_bg.set_stroke(GRAY, 1)
            bar_fill = Rectangle(width=0.9, height=0.15, fill_color=GREEN, fill_opacity=1, stroke_width=0)
            bar_fill.move_to(bar_bg.get_center())
            bar_bg.next_to(box, DOWN, buff=0.15)
            bar_fill.next_to(box, DOWN, buff=0.15)
            return VGroup(box, label, bar_bg, bar_fill)

        ticket_names = ["T1", "T2", "T3"]
        tickets = VGroup(*[make_ticket(n) for n in ticket_names])
        tickets.arrange(RIGHT, buff=0.4)
        tickets.next_to(worker_label, DOWN, buff=0.6).align_to(worker_label, LEFT)

        self.play(LaggedStartMap(FadeIn, tickets, shift=UP, lag_ratio=0.15))

        supervisor_label = Text("Supervisor", font_size=28, color=PURPLE)
        supervisor_label.to_edge(RIGHT, buff=1.2).shift(UP * 1.6)
        self.play(FadeIn(supervisor_label))

        queue_label = Text("mm:queue", font_size=24, color=GRAY)
        queue_label.to_edge(RIGHT, buff=1.6).shift(DOWN * 2.6)
        queue_box = Square(side_length=1.3)
        queue_box.set_stroke(GRAY, 2)
        queue_box.next_to(queue_label, UP, buff=0.3)
        self.play(FadeIn(queue_label), Create(queue_box))

        status = Text("worker heartbeats every 2s, refreshing TTL", font_size=26, color=GREEN)
        status.to_edge(DOWN, buff=1.6)
        self.play(FadeIn(status))

        def bar_fraction_anim(frac):
            new_bars = []
            for t in tickets:
                bg = t[2]
                new_fill = Rectangle(
                    width=max(bg.width * frac, 0.001),
                    height=0.15,
                    fill_color=GREEN if frac > 0.3 else RED,
                    fill_opacity=1,
                    stroke_width=0,
                )
                new_fill.move_to(bg.get_left(), aligned_edge=LEFT)
                new_bars.append(Transform(t[3], new_fill))
            return new_bars

        # --- Two healthy heartbeats: pulse the worker, TTL bars stay full ---
        for _ in range(2):
            self.play(
                worker_label.animate.set_color(YELLOW),
                run_time=0.2,
            )
            self.play(worker_label.animate.set_color(BLUE), run_time=0.2)
            self.play(*bar_fraction_anim(1.0), run_time=0.3)
            self.wait(0.4)

        # --- Worker crashes ---
        # Text mobjects with different content morph glyph-by-glyph under
        # Transform, which reads as garbled overlap. A simultaneous
        # FadeOut/FadeIn still cross-fades the two captions on top of each
        # other, so fade the old caption out completely before fading the
        # new one in.
        crash_status = Text("worker crashes - heartbeat stops", font_size=26, color=RED)
        crash_status.move_to(status)
        self.play(
            FadeOut(status),
            worker_label.animate.set_color(GRAY),
            *[t[0].animate.set_stroke(GRAY) for t in tickets],
            run_time=0.4,
        )
        self.play(FadeIn(crash_status), run_time=0.2)
        status = crash_status
        self.wait(0.3)

        # --- TTL counts down without refresh ---
        countdown_status = Text("lock TTL counts down (30s lease)", font_size=26, color=RED)
        countdown_status.move_to(status)
        self.play(FadeOut(status))
        self.play(FadeIn(countdown_status))
        status = countdown_status
        for frac in [0.66, 0.33, 0.05]:
            self.play(*bar_fraction_anim(frac), run_time=0.5)
            self.wait(0.2)

        # --- Supervisor scan detects expired lease ---
        scan_status = Text("supervisor scan (every 5s) checks mm:hb:* keys", font_size=26, color=PURPLE)
        scan_status.move_to(status)
        self.play(
            FadeOut(status),
            supervisor_label.animate.set_color(YELLOW),
            run_time=0.3,
        )
        self.play(FadeIn(scan_status), run_time=0.2)
        status = scan_status
        self.play(supervisor_label.animate.set_color(PURPLE), run_time=0.3)
        self.wait(0.3)

        detect_status = Text("expired lease detected - reclaiming stranded tickets", font_size=26, color=PURPLE)
        detect_status.move_to(status)
        self.play(FadeOut(status))
        self.play(FadeIn(detect_status))
        status = detect_status

        # --- Tickets move back to the queue ---
        move_anims = []
        for t in tickets:
            move_anims.append(t.animate.scale(0.6).move_to(queue_box.get_center()).set_color(GRAY))
        self.play(*move_anims, run_time=1.0)
        self.play(FadeOut(tickets), run_time=0.4)

        final_status = Text(
            "stranded tickets returned to queue - zero tickets lost",
            font_size=28,
            color=GREEN,
        )
        final_status.move_to(status)
        self.play(FadeOut(status))
        self.play(FadeIn(final_status))
        self.wait(1.5)
