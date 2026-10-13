# Qwen3.6-35B-A3B on a laptop: PolyStrata and llama.cpp b11540 (2026-10-11)

`bench/bench_vs_llama.py` with `machine-laptop.json`, three rounds, run as
[COMMUNITY_BENCHMARKS.md](../../../docs/COMMUNITY_BENCHMARKS.md#comparing-with-llamacpp) describes it. Every
request is in `raw/`, the engines' logs are in this folder, and `run.log` has each request's numbers.

- Laptop: RTX 4070 Laptop (8 GB, driver 610.74), Core i7-14700HX, 32 GB RAM, Windows 10, on mains power.
- Model: `Qwen3.6-35B-A3B-UD-Q3_K_M.gguf` (17.1 GB), the file setup downloads for the size. Its draft block (MTP)
  is in the same file, and both engines use it.
- PolyStrata: the ready-made strata-poly built from commit 2ba29a383baf ("serve: name the signal that ended the
  engine"), run with the config setup wrote for the size (`strata-cfg-polystrata-setup.json`): 13 threads, an
  8 GiB conversation cache, `--tail-skip 6` and a context of 36,864.
- llama.cpp: the Windows CUDA 13 build of b11540 from llama.cpp's releases.
  - tuned: `-ngl 99 --n-cpu-moe 30 -c 36864 -ctk q8_0 -ctv q8_0 -fa on -t 20 -ub 512`, with
    `--spec-type draft-mtp --spec-draft-n-max 2` (mtp2), `3` (mtp3) or no draft (nomtp). N = 30 is the value
    found for this file on this laptop.
  - fit: `--fit on` and the same context, cache and draft settings as tuned mtp2.

A round sends the 4K prompt twice and the 32K prompt once at temperature 0 and again at 0.7, each for up to 256
tokens of answer. Medians over the three rounds:

| config | prompt | temp | n | prompt tok/s | answer tok/s | time to first token | drafts accepted | peak VRAM MiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PolyStrata | 4K | 0 | 6 | 1,414 | 79.5 | 2.87 s | 0.71 | 7,561 |
| PolyStrata | 4K | 0.7 | 6 | 1,418 | 80.5 | 2.86 s | 0.63 | 7,561 |
| PolyStrata | 32K | 0 | 3 | 1,601 | 69.1 | 20.0 s | 0.73 | 7,561 |
| PolyStrata | 32K | 0.7 | 3 | 1,598 | 68.1 | 20.1 s | 0.74 | 7,567 |
| llama.cpp tuned mtp2 | 4K | 0 | 6 | 494 | 44.4 | 8.22 s | 0.55 | 7,655 |
| llama.cpp tuned mtp2 | 4K | 0.7 | 6 | 493 | 43.3 | 8.22 s | 0.52 | 7,655 |
| llama.cpp tuned mtp2 | 32K | 0 | 3 | 483 | 41.5 | 66.3 s | 0.57 | 7,658 |
| llama.cpp tuned mtp2 | 32K | 0.7 | 3 | 484 | 41.3 | 66.3 s | 0.57 | 7,669 |
| llama.cpp tuned mtp3 | 4K | 0 | 6 | 499 | 42.9 | 8.13 s | 0.44 | 7,702 |
| llama.cpp tuned mtp3 | 4K | 0.7 | 6 | 499 | 43.3 | 8.13 s | 0.43 | 7,723 |
| llama.cpp tuned mtp3 | 32K | 0 | 3 | 483 | 37.6 | 66.3 s | 0.53 | 7,723 |
| llama.cpp tuned mtp3 | 32K | 0.7 | 3 | 483 | 39.8 | 66.4 s | 0.56 | 7,723 |
| llama.cpp tuned nomtp | 4K | 0 | 6 | 517 | 44.4 | 7.85 s | - | 6,956 |
| llama.cpp tuned nomtp | 4K | 0.7 | 6 | 517 | 44.3 | 7.85 s | - | 6,956 |
| llama.cpp tuned nomtp | 32K | 0 | 3 | 502 | 39.2 | 63.9 s | - | 6,963 |
| llama.cpp tuned nomtp | 32K | 0.7 | 3 | 504 | 40.3 | 63.5 s | - | 6,963 |
| llama.cpp fit mtp2 | 4K | 0 | 6 | 479 | 46.0 | 8.47 s | 0.58 | 6,542 |
| llama.cpp fit mtp2 | 4K | 0.7 | 6 | 480 | 42.1 | 8.44 s | 0.47 | 6,542 |
| llama.cpp fit mtp2 | 32K | 0 | 3 | 466 | 39.6 | 68.7 s | 0.54 | 6,548 |
| llama.cpp fit mtp2 | 32K | 0.7 | 3 | 464 | 39.3 | 69.0 s | 0.58 | 6,548 |

Against the fastest llama.cpp row of each cell, PolyStrata read the prompt 2.7 times as fast at 4K and 3.2 times
at 32K, and wrote 1.7 to 1.8 times as fast. The peak VRAM is the whole card's, with the 430 to 460 MiB the
desktop used before the engine started. The process's peak RAM was 16 to 19 GiB for llama.cpp and 18 to 20 GiB
for PolyStrata (`summary` prints it).
