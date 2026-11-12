"""Check device selection and inference without downloading model weights."""

import math
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

import torch
from transformers import GPT2Config, GPT2LMHeadModel

import binoculars_signal
import config
import detector


class ModelDeviceTests(unittest.TestCase):
    def test_auto_selects_cuda_then_mps_then_cpu(self):
        for cuda, mps, expected in [(True, True, "cuda"), (False, True, "mps"),
                                    (False, False, "cpu")]:
            with self.subTest(cuda=cuda, mps=mps), patch.object(
                config, "INFERENCE_DEVICE", "auto"
            ), patch("torch.cuda.is_available", return_value=cuda), patch(
                "torch.backends.mps.is_available", return_value=mps
            ):
                self.assertEqual(detector.inference_device().type, expected)

    def test_explicit_device_overrides_auto_selection(self):
        for device in ["cpu", "cuda", "mps"]:
            with self.subTest(device=device), patch.object(
                config, "INFERENCE_DEVICE", device
            ), patch("torch.cuda.is_available", return_value=True), patch(
                "torch.backends.mps.is_available", return_value=True
            ):
                self.assertEqual(detector.inference_device().type, device)

    def test_unavailable_or_unknown_device_is_not_silently_replaced(self):
        for device in ["cuda", "mps", "invalid"]:
            with self.subTest(device=device), patch.object(
                config, "INFERENCE_DEVICE", device
            ), patch("torch.cuda.is_available", return_value=False), patch(
                "torch.backends.mps.is_available", return_value=False
            ):
                with self.assertRaises(detector.DetectorUnavailable):
                    detector.inference_device()

    def test_both_scoring_paths_run_on_available_devices(self):
        # Tiny real models exercise tensor placement and loss calculation.
        # CPU always runs; accelerator coverage is enabled where available.
        devices = ["cpu"]
        if torch.backends.mps.is_available():
            devices.append("mps")
        if torch.cuda.is_available():
            devices.append("cuda")

        class Tokenizer:
            def get_vocab(self):
                return {str(i): i for i in range(32)}

            def __call__(self, text, **kwargs):
                return {"input_ids": torch.tensor([[1, 2, 3, 4]])}

        tiny_config = GPT2Config(vocab_size=32, n_positions=16, n_embd=16,
                                 n_layer=1, n_head=2)
        for device in devices:
            with self.subTest(device=device), patch.object(
                config, "INFERENCE_DEVICE", device
            ), patch.object(config, "BINOCULARS_ENABLED", True), patch.object(detector, "_model", None), patch.object(
                detector, "_tokenizer", None
            ), patch.object(binoculars_signal, "_performer", None), patch.object(
                binoculars_signal, "PERFORMER", "test-performer"
            ), patch("transformers.AutoTokenizer.from_pretrained", return_value=Tokenizer()), patch(
                "transformers.AutoModelForCausalLM.from_pretrained",
                side_effect=[GPT2LMHeadModel(tiny_config), GPT2LMHeadModel(tiny_config)],
            ):
                self.assertTrue(math.isfinite(detector.perplexity("Example text.")))
                self.assertTrue(math.isfinite(binoculars_signal.binoculars_score("Example text.")["B"]))
                for score in [detector.model_signal("Example text."),
                              binoculars_signal.binoculars_signal("Example text.")]:
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 1)
                self.assertEqual(detector._model.device.type, device)
                self.assertEqual(binoculars_signal._performer.device.type, device)


class BinocularsDisableTests(unittest.TestCase):
    def test_environment_switch_defaults_on_and_accepts_explicit_off(self):
        for value, expected in ((None, True), ("0", False), ("1", True)):
            with self.subTest(value=value), patch.dict(os.environ):
                if value is None:
                    os.environ.pop("AI201_BINOCULARS", None)
                else:
                    os.environ["AI201_BINOCULARS"] = value
                settings = runpy.run_path(str(Path(__file__).with_name("config.py")))
                self.assertIs(settings["BINOCULARS_ENABLED"], expected)

    def test_disabled_library_calls_do_not_load_or_run_models(self):
        calls = (
            lambda: binoculars_signal.binoculars_score("Example text."),
            lambda: binoculars_signal.binoculars_signal("Example text."),
            binoculars_signal.warm_up,
            binoculars_signal._load_performer,
        )
        with patch.object(config, "BINOCULARS_ENABLED", False), patch(
            "detector._load"
        ) as load, patch.object(binoculars_signal, "_performer", object()):
            for call in calls:
                with self.assertRaisesRegex(detector.DetectorUnavailable, "Binoculars is disabled"):
                    call()
            load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
