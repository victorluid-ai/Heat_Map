import numpy as np
import pytest

from src.heatmap.accumulator import HeatmapAccumulator
from src.heatmap.floor_plan import FloorPlan
from src.heatmap.kde_renderer import KDERenderer


def test_accumulator_starts_empty(accumulator):
    assert accumulator.total_updates == 0


def test_add_point_increments_counter(accumulator):
    accumulator.add_point(50.0, 40.0)
    assert accumulator.total_updates == 1
    accumulator.add_point(10.0, 10.0)
    assert accumulator.total_updates == 2


def test_get_heatmap_image_returns_correct_shape(accumulator, small_floor_plan):
    h, w = small_floor_plan.height, small_floor_plan.width
    image = accumulator.get_heatmap_image()
    assert image.shape == (h, w, 3)
    assert image.dtype == np.uint8


def test_get_heatmap_image_with_heat(accumulator):
    accumulator.add_point(50.0, 40.0, weight=100.0)
    image = accumulator.get_heatmap_image()
    assert image is not None
    assert image.max() > 0


def test_decay_reduces_heat(accumulator):
    accumulator.add_point(50.0, 40.0, weight=1000.0)
    before = accumulator._heat.max()
    accumulator.decay()
    after = accumulator._heat.max()
    assert after < before


def test_floor_plan_blank_canvas(small_floor_plan):
    img = small_floor_plan.image
    assert img.shape == (small_floor_plan.height, small_floor_plan.width, 3)
    assert np.all(img == 0)


def test_kde_renderer_returns_correct_shape(small_floor_plan):
    renderer = KDERenderer(small_floor_plan, bandwidth=5)
    points = [(20.0, 30.0), (50.0, 40.0), (80.0, 60.0)]
    image = renderer.render(points)
    assert image.shape == (small_floor_plan.height, small_floor_plan.width, 3)
    assert image.dtype == np.uint8


def test_kde_renderer_empty_points_returns_base(small_floor_plan):
    renderer = KDERenderer(small_floor_plan, bandwidth=5)
    image = renderer.render([])
    assert image.shape == (small_floor_plan.height, small_floor_plan.width, 3)
