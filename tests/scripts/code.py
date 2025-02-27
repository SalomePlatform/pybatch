from pathlib import Path

txt = Path("input.txt").read_text()
v1 = int(txt)
r1 = v1 + 9
Path("output.txt").write_text(str(r1))

txt = (Path("data") / "input.txt").read_text()
v2 = int(txt)
r2 = v2 + 9
(Path("data") / "output.txt").write_text(str(r2))
