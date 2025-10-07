import os
import warnings
from io import BytesIO

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def compare_snapshot(baseline_path, actual_image):
    baseline_image = Image.open(baseline_path).convert("L")
    actual_image = actual_image.convert("L")

    min_width = min(actual_image.width, baseline_image.width)
    min_height = min(actual_image.height, baseline_image.height)

    actual_cropped = actual_image.crop((0, 0, min_width, min_height))
    expected_cropped = baseline_image.crop((0, 0, min_width, min_height))

    actual_np = np.array(actual_cropped, dtype=np.uint8)
    expected_np = np.array(expected_cropped, dtype=np.uint8)

    if actual_np.shape != expected_np.shape:
        warnings.warn(f"Actual shape: {actual_np.shape}")
        warnings.warn(f"Expected shape: {expected_np.shape}")
        raise ValueError("Image sizes do not match")

    win_size = min(min(actual_np.shape[0:2]), 7)
    if win_size % 2 == 0:
        win_size -= 1

    score, _diff = ssim(
        actual_np, expected_np, full=True, win_size=win_size, channel_axis=-1
    )
    return score >= 0.98, score


def assert_matches_snapshot(snapshot, device, page_name):
    baseline_path = f"snapshots/{device}/{page_name}"
    screenshot_image = Image.open(BytesIO(snapshot))

    if not os.path.exists(baseline_path):
        print(
            "Baseline snapshot not found — saving current screenshot as baseline."
        )
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        screenshot_image.save(baseline_path)
        return

    result, score = compare_snapshot(baseline_path, screenshot_image)

    if not result:
        screenshot_image.save(baseline_path)
        raise AssertionError(
            f"{page_name} has changed. Similarity score: {score}. Overwiting baseline snapshot."
        )
