import os
import warnings
from io import BytesIO

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def compare_snapshot(baseline_path, screenshot_image):
    baseline_image = Image.open(baseline_path)

    # ensure both images have the same dimensions
    min_width = min(baseline_image.width, screenshot_image.width)
    min_height = min(baseline_image.height, screenshot_image.height)

    baseline_cropped = baseline_image.crop((0, 0, min_width, min_height))
    screenshot_cropped = screenshot_image.crop((0, 0, min_width, min_height))

    baseline_np = np.array(baseline_cropped, dtype=np.uint8)
    screenshot_np = np.array(screenshot_cropped, dtype=np.uint8)

    if baseline_np.shape != screenshot_np.shape:
        warnings.warn(f"Baseline shape: {baseline_np.shape}")
        warnings.warn(f"Screenshot shape: {screenshot_np.shape}")
        raise ValueError("Image sizes do not match")

    # dynamically adjust win_size based on image dimensions
    min_side = min(baseline_np.shape[0], baseline_np.shape[1])
    win_size = min(7, min_side)
    if win_size % 2 == 0:
        win_size -= 1

    score, _diff = ssim(
        baseline_np, screenshot_np, full=True, win_size=win_size
    )
    return score >= 0.9, score


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
        print(
            f"\n{page_name} has changed ({score}). Updating baseline snapshot."
        )
        screenshot_image.save(baseline_path)
        return

    print(f"No changes detected for {page_name} (score: {score}).")
