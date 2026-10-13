"""Tests for setup.py's ready-made strata-poly (get_poly_prebuilt) from a local release folder: the asset of this
source is installed, one for another source or another card is not, and an engine already there is kept.  No GPU,
no network, no pip.

    python -m unittest tools.test_poly_prebuilt
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import setup  # noqa: E402

SRC = "0123456789abcdef"
GPU = {"arch": 89, "driver": "581.57"}


def release(folder: Path, src=SRC, archs=(75, 80, 86, 89, 120)) -> None:
    with zipfile.ZipFile(folder / setup.POLY_ASSET.format(src=src), "w") as f:
        f.writestr(setup.POLY_EXE, "new engine")
        f.writestr(setup.VEXE, "new encoder")
        f.writestr("BUILD.json", json.dumps({"source": "release", "archs": list(archs), "cuda": "13.0", "src": src,
                                             "vision_src": src}))


class PolyPrebuilt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.rel = Path(self.tmp.name) / "release"
        self.root.mkdir()
        self.rel.mkdir()
        self.eng = self.root / setup.ENGINE_POLY_DIR
        for p in (mock.patch.object(setup, "ROOT", self.root), mock.patch.object(setup, "WIN", True),
                  mock.patch.object(setup, "POLY_PREBUILT_URL", str(self.rel)),
                  mock.patch.object(setup, "source_hash", lambda parts: SRC),
                  mock.patch.object(setup, "cpu_info", lambda: ("an AVX2 CPU", True, False)),
                  mock.patch.object(setup, "pip_cuda_libs", lambda toolkit=13: None)):
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_installs_the_asset_of_this_source(self):
        release(self.rel)
        self.assertTrue(setup.get_poly_prebuilt(GPU))
        self.assertEqual((self.eng / setup.POLY_EXE).read_text(), "new engine")
        self.assertEqual((self.eng / setup.VEXE).read_text(), "new encoder")
        self.assertEqual(json.loads((self.eng / "BUILD.json").read_text())["source"], "release")
        self.assertEqual(sorted(p.name for p in self.eng.iterdir()), sorted(["BUILD.json", setup.POLY_EXE, setup.VEXE]))

    def test_none_for_another_source(self):
        release(self.rel, src="fedcba9876543210")
        self.assertFalse(setup.get_poly_prebuilt(GPU))
        self.assertFalse((self.eng / setup.POLY_EXE).exists())

    def test_none_for_a_card_it_has_no_code_for(self):
        release(self.rel)
        self.assertFalse(setup.get_poly_prebuilt({"arch": 90, "driver": "581.57"}))
        self.assertFalse((self.eng / setup.POLY_EXE).exists())

    def test_none_with_a_driver_older_than_cuda_13(self):
        release(self.rel)
        self.assertFalse(setup.get_poly_prebuilt({"arch": 89, "driver": "576.88"}))

    def test_none_for_a_cpu_without_avx2(self):
        release(self.rel)
        with mock.patch.object(setup, "cpu_info", lambda: ("an older CPU", False, False)):
            self.assertFalse(setup.get_poly_prebuilt(GPU))

    def test_a_failed_pip_leaves_the_engine_there(self):
        self.eng.mkdir()
        (self.eng / setup.POLY_EXE).write_text("compiled here")
        release(self.rel)
        with mock.patch.object(setup, "pip_cuda_libs", side_effect=SystemExit(1)):
            with self.assertRaises(SystemExit):
                setup.get_poly_prebuilt(GPU)
        self.assertEqual((self.eng / setup.POLY_EXE).read_text(), "compiled here")

    def test_an_update_downloads_in_place_of_a_ready_made_engine_alone(self):
        release(self.rel)
        self.eng.mkdir()
        cfg = {"exe": str(self.eng / setup.POLY_EXE), "args": []}
        for source, want in (("local", "compiled here"), ("release", "new engine")):
            (self.eng / setup.POLY_EXE).write_text("compiled here")
            (self.eng / "BUILD.json").write_text(json.dumps({"source": source, "archs": [89], "src": "older"}))
            with mock.patch.object(setup, "gpu_info", lambda i=None: GPU), \
                    mock.patch.object(setup, "build_engine_poly", lambda *a: self.eng), \
                    mock.patch.object(setup, "get_llama_cpp", lambda: None):
                setup.update_poly_engine(dict(cfg))
            self.assertEqual((self.eng / setup.POLY_EXE).read_text(), want, source)

    def test_an_update_without_a_release_of_its_source_keeps_the_ready_made_engine(self):
        release(self.rel, src="fedcba9876543210")
        self.eng.mkdir()
        (self.eng / setup.POLY_EXE).write_text("ready-made")
        (self.eng / "BUILD.json").write_text(json.dumps({"source": "release", "archs": [89], "src": "older"}))
        build = mock.Mock()
        with mock.patch.object(setup, "gpu_info", lambda i=None: GPU), \
                mock.patch.object(setup, "build_engine_poly", build):
            setup.update_poly_engine({"exe": str(self.eng / setup.POLY_EXE), "args": []})
        build.assert_not_called()
        self.assertEqual((self.eng / setup.POLY_EXE).read_text(), "ready-made")

    def test_a_ready_made_engine_with_an_older_encoder_is_replaced(self):
        release(self.rel)
        self.eng.mkdir()
        (self.eng / setup.POLY_EXE).write_text("ready-made")
        (self.eng / "BUILD.json").write_text(json.dumps({"source": "release", "archs": [89], "src": SRC,
                                                         "vision_src": "older"}))
        self.assertTrue(setup.get_poly_prebuilt(GPU))
        self.assertEqual((self.eng / setup.VEXE).read_text(), "new encoder")

    def test_an_engine_of_this_source_is_kept(self):
        self.eng.mkdir()
        (self.eng / setup.POLY_EXE).write_text("compiled here")
        (self.eng / "BUILD.json").write_text(json.dumps({"source": "local", "archs": [89], "src": SRC}))
        release(self.rel)
        self.assertTrue(setup.get_poly_prebuilt(GPU))
        self.assertEqual((self.eng / setup.POLY_EXE).read_text(), "compiled here")

    def test_a_compile_after_it_is_for_this_card_alone(self):
        release(self.rel)
        setup.get_poly_prebuilt(GPU)
        meta = json.loads((self.eng / "BUILD.json").read_text())
        meta["src"] = "a source it was not built from"
        (self.eng / "BUILD.json").write_text(json.dumps(meta))
        with mock.patch.object(setup, "install_build_tools", side_effect=RuntimeError("compiles")) as tools:
            with self.assertRaises(RuntimeError):
                setup.build_engine_poly(GPU, True, None)
        self.assertEqual(tools.call_args[0][0]["archs"], [89])


if __name__ == "__main__":
    unittest.main()
