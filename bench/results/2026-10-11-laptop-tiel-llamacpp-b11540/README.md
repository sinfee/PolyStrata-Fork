# Tiel Coder 35B-A3B on a laptop: PolyStrata and llama.cpp b11540 (2026-10-11)

`bench/bench_vs_llama.py` with `machine-laptop.json`, three rounds, run as
[COMMUNITY_BENCHMARKS.md](../../../docs/COMMUNITY_BENCHMARKS.md#comparing-with-llamacpp) describes it. Every
request is in `raw/`, the engines' logs are in this folder, and `run.log` has each request's numbers.

- Laptop: RTX 4070 Laptop (8 GB, driver 610.74), Core i7-14700HX, 32 GB RAM, Windows 10, on mains power.
- Model: `Tiel-Coder-35B-A3B-MTP-UD-Q3_K_XL.gguf` (17.2 GB), the file setup downloads for the size. Its draft block
  (MTP) is in the same file, and both engines use it.
- PolyStrata: the ready-made strata-poly built from commit 2ba29a383baf ("serve: name the signal that ended the
  engine"), run with the config setup wrote for the size (`strata-cfg-polystrata-setup.json`): 13 threads, an
  8 GiB conversation cache and a context of 36,864.
- llama.cpp: the Windows CUDA 13 build of b11540 from llama.cpp's releases.
  - tuned: `-ngl 99 --n-cpu-moe 30 -c 36864 -ctk q8_0 -ctv q8_0 -fa on -t 20 -ub 512`, with
    `--spec-type draft-mtp --spec-draft-n-max 2` (mtp2), `3` (mtp3) or no draft (nomtp). N = 30 is the value
    found for Qwen3.6 UD-Q3_K_M on this laptop, a file of about the same size; it was not searched again for
    this one.
  - fit: `--fit on` and the same context, cache and draft settings as tuned mtp2.

A round sends the 4K prompt twice and the 32K prompt once at temperature 0 and again at 0.7, each for up to 256
tokens of answer. Medians over the three rounds:

| config | prompt | temp | n | prompt tok/s | answer tok/s | time to first token | drafts accepted | peak VRAM MiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PolyStrata | 4K | 0 | 6 | 1,378 | 71.2 | 3.07 s | 0.64 | 7,556 |
| PolyStrata | 4K | 0.7 | 6 | 1,377 | 76.7 | 3.07 s | 0.67 | 7,556 |
| PolyStrata | 32K | 0 | 3 | 1,598 | 62.4 | 20.2 s | 0.70 | 7,561 |
| PolyStrata | 32K | 0.7 | 3 | 1,596 | 62.9 | 20.2 s | 0.72 | 7,574 |
| llama.cpp tuned mtp2 | 4K | 0 | 6 | 450 | 45.8 | 9.41 s | 0.50 | 7,556 |
| llama.cpp tuned mtp2 | 4K | 0.7 | 6 | 450 | 43.9 | 9.41 s | 0.44 | 7,556 |
| llama.cpp tuned mtp2 | 32K | 0 | 3 | 451 | 40.1 | 71.5 s | 0.51 | 7,556 |
| llama.cpp tuned mtp2 | 32K | 0.7 | 3 | 451 | 42.0 | 71.5 s | 0.55 | 7,556 |
| llama.cpp tuned mtp3 | 4K | 0 | 6 | 449 | 38.3 | 9.43 s | 0.33 | 7,612 |
| llama.cpp tuned mtp3 | 4K | 0.7 | 6 | 449 | 40.1 | 9.42 s | 0.37 | 7,617 |
| llama.cpp tuned mtp3 | 32K | 0 | 3 | 451 | 33.5 | 71.5 s | 0.33 | 7,617 |
| llama.cpp tuned mtp3 | 32K | 0.7 | 3 | 451 | 36.2 | 71.5 s | 0.39 | 7,617 |
| llama.cpp tuned nomtp | 4K | 0 | 6 | 456 | 45.1 | 9.28 s | - | 6,896 |
| llama.cpp tuned nomtp | 4K | 0.7 | 6 | 456 | 44.8 | 9.29 s | - | 6,896 |
| llama.cpp tuned nomtp | 32K | 0 | 3 | 456 | 39.5 | 70.7 s | - | 6,896 |
| llama.cpp tuned nomtp | 32K | 0.7 | 3 | 456 | 39.2 | 70.7 s | - | 6,896 |
| llama.cpp fit mtp2 | 4K | 0 | 6 | 424 | 42.7 | 9.97 s | 0.47 | 6,520 |
| llama.cpp fit mtp2 | 4K | 0.7 | 6 | 425 | 41.2 | 9.96 s | 0.44 | 6,521 |
| llama.cpp fit mtp2 | 32K | 0 | 3 | 423 | 40.5 | 76.2 s | 0.58 | 6,521 |
| llama.cpp fit mtp2 | 32K | 0.7 | 3 | 423 | 37.7 | 76.2 s | 0.50 | 6,525 |

Against the fastest llama.cpp row of each cell, PolyStrata read the prompt 3.0 times as fast at 4K and 3.5 times
at 32K, and wrote 1.5 to 1.7 times as fast. The peak VRAM is the whole card's, with the 435 to 457 MiB the
desktop used before the engine started. The process's peak RAM was 17 to 19 GiB for llama.cpp and 18 to 20 GiB
for PolyStrata (`summary` prints it).
