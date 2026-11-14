from manim import *
from scenekit import *

LINE = "#2E332F"
OLD, NEW = "1.64.1", "1.65.1"


def code(s, size=22, color=PRIMARY, **kw):
    esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return MarkupText(f'<span font_features="calt 0, liga 0">{esc}</span>', font=MONO, font_size=size, color=color, **kw)


def square(size=0.34, color=LINE, opacity=0.35):
    sq = RoundedRectangle(corner_radius=0.05, width=size, height=size, color=color, stroke_width=2)
    return sq.set_fill(color, opacity=opacity)


def shards(n=16, size=0.34, buff=0.1):
    return VGroup(*[square(size) for _ in range(n)]).arrange(RIGHT, buff=buff)


def paint(sq, color, opacity=0.35):
    return sq.animate.set_stroke(color).set_fill(color, opacity=opacity)


def paint_all(row, color, lag=0.03, opacity=0.35):
    return LaggedStart(*[paint(sq, color, opacity) for sq in row], lag_ratio=lag)


class S1Result(Timed):
    def construct(self):
        title = code("npx playwright test --shard=k/16", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        hook = VGroup(
            txt("Playwright tests split across shards?", 40),
            code("the newest release can turn green red", 26, ACCENT),
        ).arrange(DOWN, buff=0.45).move_to([0, 0.3, 0])
        self.play(FadeIn(hook[0], shift=UP * 0.2), run_time=0.5)
        self.at("the newest release")
        self.play(FadeIn(hook[1], shift=UP * 0.15), run_time=0.4)
        first = self.cue("filter that matches")
        self.cursor = 0
        self.wait(first - 0.6 - self.now())
        self.play(FadeOut(hook), run_time=0.35)

        cond = code("filter matches 0 tests", 26, ACCENT).move_to([0, 2.2, 0])
        old_lab = code(OLD, 24, DIM).move_to([-5.4, 0.9, 0], aligned_edge=LEFT)
        new_lab = code(NEW, 24, DIM).move_to([-5.4, -0.5, 0], aligned_edge=LEFT)
        old_row = shards().move_to([0.6, 0.9, 0])
        new_row = shards().move_to([0.6, -0.5, 0])
        self.at("filter that matches")
        self.play(FadeIn(cond, shift=UP * 0.15), run_time=0.4)
        self.at("used to pass")
        self.play(FadeIn(old_lab), LaggedStart(*[FadeIn(sq, scale=0.6) for sq in old_row], lag_ratio=0.03), run_time=0.6)
        self.play(paint_all(old_row, GOOD), run_time=0.6)
        self.at("on version")
        self.play(FadeIn(new_lab), LaggedStart(*[FadeIn(sq, scale=0.6) for sq in new_row], lag_ratio=0.03), run_time=0.6)
        self.at("every shard fails")
        self.play(paint_all(new_row, BAD, opacity=0.45), run_time=0.7)
        count = code("16 shards  ·  16 red jobs", 28, BAD).move_to([0.6, -1.5, 0])
        self.at("sixteen shards")
        self.play(FadeIn(count, shift=UP * 0.15), run_time=0.4)
        tease = VGroup(txt("what changed", 30), code("·", 26, DIM), txt("what did not", 30, ACCENT)).arrange(RIGHT, buff=0.3)
        tease.move_to([0, -2.7, 0])
        self.at("here is what")
        self.play(FadeIn(tease, shift=UP * 0.15), run_time=0.4)
        self.end()


class S2Setup(Timed):
    def construct(self):
        title = code("the experiment", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        suite = VGroup(*[square(0.26) for _ in range(32)]).arrange_in_grid(rows=4, cols=8, buff=0.08).move_to([-4.2, 1.0, 0])
        suite_lab = code("32 tests", 22, DIM).next_to(suite, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(sq, scale=0.6) for sq in suite], lag_ratio=0.02), FadeIn(suite_lab), run_time=0.8)
        versions = VGroup(card(OLD, DIM, w=2.2, h=0.8, size=26), card(NEW, NOTE, w=2.2, h=0.8, size=26)).arrange(RIGHT, buff=0.5)
        versions.move_to([2.2, 1.5, 0])
        self.at("two playwright versions")
        self.play(FadeIn(versions[0], shift=UP * 0.15), run_time=0.4)
        self.at("the new one")
        self.play(FadeIn(versions[1], shift=UP * 0.15), run_time=0.4)
        sel = code("selected tests   0  1  2  4  8  16", 24).move_to([-0.6, -0.1, 0], aligned_edge=LEFT)
        shd = code("shards           2  4  8  16", 24).move_to([-0.6, -0.8, 0], aligned_edge=LEFT)
        self.at("selects between")
        self.play(FadeIn(sel, shift=RIGHT * 0.15), run_time=0.4)
        self.at("splits them")
        self.play(FadeIn(shd, shift=RIGHT * 0.15), run_time=0.4)
        total = code("1,464 runs", 64, PRIMARY).move_to([0, -2.2, 0])
        note = code("exit code of every run recorded", 22, DIM).next_to(total, DOWN, buff=0.3)
        self.at("one thousand")
        self.play(FadeIn(total, shift=UP * 0.2), run_time=0.5)
        self.at("exit code")
        self.play(FadeIn(note), run_time=0.4)
        self.end()


class S3Zero(Timed):
    def construct(self):
        title = code("0 tests selected", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        lx, ox, nx = -5.8, -1.2, 3.6
        heads = VGroup(code(OLD, 24, DIM).move_to([ox, 2.2, 0]), code(NEW, 24, NOTE).move_to([nx, 2.2, 0]))
        rows = VGroup(
            code("no shards", 24).move_to([lx, 1.0, 0], aligned_edge=LEFT),
            code("16 shards", 24).move_to([lx, -0.9, 0], aligned_edge=LEFT),
        )
        single = VGroup(square(0.5).move_to([ox, 1.0, 0]), square(0.5).move_to([nx, 1.0, 0]))
        self.play(FadeIn(heads), FadeIn(rows[0]), FadeIn(single), run_time=0.5)
        err = VGroup(*[code("No tests found", 18, BAD).next_to(sq, DOWN, buff=0.2) for sq in single])
        self.at("both versions fail")
        self.play(*[paint(sq, BAD, 0.45) for sq in single], run_time=0.5)
        self.at("no tests found")
        self.play(FadeIn(err), run_time=0.4)

        old_row = shards(size=0.2, buff=0.06).move_to([ox, -0.9, 0])
        new_row = shards(size=0.2, buff=0.06).move_to([nx, -0.9, 0])
        self.at("add shards")
        self.play(FadeIn(rows[1]), FadeIn(old_row), FadeIn(new_row), run_time=0.5)
        self.at("every shard passes")
        self.play(paint_all(old_row, GOOD), run_time=0.6)
        hid = code("sharding hid the error", 20, WARN).next_to(old_row, DOWN, buff=0.3)
        self.at("sharding hid")
        self.play(FadeIn(hid, shift=UP * 0.1), run_time=0.4)
        self.at("every shard fails")
        self.play(paint_all(new_row, BAD, opacity=0.45), run_time=0.6)
        same = code("same as the unsharded run", 20, BAD).next_to(new_row, DOWN, buff=0.3)
        self.at("the same as")
        self.play(FadeIn(same, shift=UP * 0.1), run_time=0.4)
        self.end()


class S4Empty(Timed):
    def construct(self):
        title = code("1 test selected  ·  16 shards", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        row = shards(size=0.5, buff=0.14).move_to([0, 1.0, 0])
        self.play(LaggedStart(*[FadeIn(sq, scale=0.6) for sq in row], lag_ratio=0.03), run_time=0.6)
        test = Dot(radius=0.1, color=PRIMARY).move_to(row[0])
        one = code("1 test", 20).next_to(row[0], UP, buff=0.25)
        self.at("spread one test")
        self.play(FadeIn(test, scale=0.5), FadeIn(one), run_time=0.4)
        empty = code("15 empty shards", 20, DIM).next_to(VGroup(*row[1:]), UP, buff=0.25)
        self.at("fifteen have nothing")
        self.play(FadeIn(empty), run_time=0.4)
        self.at("all of them pass")
        self.play(paint_all(row, GOOD), run_time=0.7)
        both = VGroup(code(f"{OLD}  pass", 24, GOOD), code(f"{NEW}  pass", 24, GOOD)).arrange(RIGHT, buff=1.0).move_to([0, -0.3, 0])
        self.at("on both versions")
        self.play(FadeIn(both, shift=UP * 0.15), run_time=0.4)
        jobs = code("180 jobs  ·  0 failed shards", 40, PRIMARY).move_to([0, -1.9, 0])
        scope = code("every run with 1 to 16 tests selected", 20, DIM).next_to(jobs, DOWN, buff=0.3)
        self.at("one hundred and eighty")
        self.play(FadeIn(jobs, shift=UP * 0.2), FadeIn(scope), run_time=0.5)
        self.end()


class S5Exception(Timed):
    def construct(self):
        title = code("the case that slips through", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        cmd = code("npx playwright test --last-failed", 30, ACCENT).move_to([0, 2.0, 0])
        when = code("after a green run, last run file restored", 20, DIM).next_to(cmd, DOWN, buff=0.3)
        self.at("rerunning only")
        self.play(FadeIn(cmd, shift=UP * 0.15), run_time=0.4)
        self.at("after a green run")
        self.play(FadeIn(when), run_time=0.4)
        lx = -5.2
        a_lab = code("no shards", 24).move_to([lx, 0.1, 0], aligned_edge=LEFT)
        a_res = code("exit 1   No tests found", 24, BAD).move_to([-1.6, 0.1, 0], aligned_edge=LEFT)
        b_lab = code("--shard=1/2", 24).move_to([lx, -1.1, 0], aligned_edge=LEFT)
        b_res = code("exit 0   0 tests run", 24, WARN).move_to([-1.6, -1.1, 0], aligned_edge=LEFT)
        self.at("without shards")
        self.play(FadeIn(a_lab), run_time=0.3)
        self.at("it fails")
        self.play(FadeIn(a_res, shift=RIGHT * 0.15), run_time=0.4)
        self.at("with shards")
        self.play(FadeIn(b_lab), run_time=0.3)
        self.at("runs nothing")
        self.play(FadeIn(b_res, shift=RIGHT * 0.15), run_time=0.4)
        note = code("same on 1.64.1 and 1.65.1", 20, DIM).move_to([0, -2.4, 0])
        self.at("still exits zero")
        self.play(FadeIn(note), run_time=0.4)
        self.end()


class S6Fix(Timed):
    def construct(self):
        title = code("what an empty run means", 22, DIM).to_edge(UP, buff=0.7)
        self.add(title)
        lx = -5.6
        a_if = txt("An empty run is normal", 30).move_to([lx, 1.7, 0], aligned_edge=LEFT)
        a_do = code("add --pass-with-no-tests", 26, GOOD).move_to([lx, 1.0, 0], aligned_edge=LEFT)
        b_if = txt("An empty run means a broken filter", 30).move_to([lx, -0.2, 0], aligned_edge=LEFT)
        b_do = code("leave the flag off  →  1.65 fails the build", 26, BAD).move_to([lx, -0.9, 0], aligned_edge=LEFT)
        self.at("if it is normal")
        self.play(FadeIn(a_if, shift=RIGHT * 0.15), run_time=0.4)
        self.at("add the pass")
        self.play(FadeIn(a_do, shift=RIGHT * 0.15), run_time=0.4)
        self.at("if it means")
        self.play(FadeIn(b_if, shift=RIGHT * 0.15), run_time=0.4)
        self.at("leave the flag off")
        self.play(FadeIn(b_do, shift=RIGHT * 0.15), run_time=0.4)
        caveat = code("caveat: 32 tests, no browser. Check your own pipeline.", 22, ACCENT).move_to([lx, -2.5, 0], aligned_edge=LEFT)
        self.at("one caveat")
        self.play(FadeIn(caveat, shift=UP * 0.1), run_time=0.4)
        self.end()


class S7EndCard(Timed):
    DRIFT = 0

    def construct(self):
        # Right half stays empty for YouTube's end-screen elements
        brand = VGroup(Dot(radius=0.1, color=GOOD), code("gary-parker", 24, GOOD)).arrange(RIGHT, buff=0.2)
        brand.move_to([-6.1, 3.0, 0], aligned_edge=LEFT)
        rows = VGroup()
        for key, value in [
            ("SOURCE", "github.com/qa-gary-parker/\npoc-playwright-empty-shards"),
            ("WRITE-UP", "garyparker.dev/blog/\nplaywright-165-empty-shards"),
        ]:
            rows.add(VGroup(code(key, 16, DIM), code(value, 24, line_spacing=0.8)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT).next_to(brand, DOWN, buff=0.9).align_to(brand, LEFT)
        summary = code("0 matching tests: 1.64.1 passes, 1.65.1 fails", 20, DIM).move_to([-6.1, -3.0, 0], aligned_edge=LEFT)
        self.add(brand, rows, summary)
        self.end(minimum=10.0)
