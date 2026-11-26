"""PySide6 user interface for Prime Grid Atlas v1.0.0."""

import csv
import json
from pathlib import Path
import traceback

import numpy as np
from PySide6.QtCore import QObject, QRectF, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QVector3D,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from atlas_engine import (
    GridConfig,
    PLACEMENTS,
    analysis_values,
    clear_volume_cache,
    current_overlay_metrics,
    fft_spectrum,
    overlay_metrics,
    placement_geometry_metrics,
    projection,
    _overlay_operation_memory_estimate,
    _projection_operation_memory_estimate,
)
from app_config import (
    AppConfig,
    config_dict,
    get_config,
    load_config,
    load_default_config_if_present,
    reset_config,
    save_config,
    set_config,
)
from compute_backend import (
    backend_error,
    backend_state,
    backend_summary,
    configure_backend,
    release_gpu_caches,
)
from metrics import entropy_edge_mask
from memory_policy import (
    MemoryBudgetExceeded,
    MemoryEstimate,
    compose_estimates,
    estimate_3d,
    estimate_scan,
    require_memory,
)
from mode_catalog import MODE_GROUPS, PRIME_MODES
from grid_model import spherical_shell_positions
from provenance import (
    ExportConsistencyGuard,
    collect_environment,
    collect_source_identity,
    finalize_experiment_manifest,
    new_experiment_manifest,
    manifest_sidecar_path,
    utc_now,
    write_manifest_atomic,
)


APP_VERSION = "1.0.0"
PROJECT_ROOT = Path(__file__).resolve().parent
PROVENANCE_SOURCE_FILES = (
    "provenance.py",
    "qt_app.py",
    "atlas_engine.py",
    "app_config.py",
    "compute_backend.py",
    "grid_model.py",
    "metrics.py",
    "number_theory.py",
)


def _grid_configuration(config, plane, depth, overlay, view=None):
    result = {
        "grid": {
            "x": config.x,
            "y": config.y,
            "z": config.z,
            "mode": config.mode,
            "mode_parameter": config.param,
            "placement": config.placement,
            "placement_parameter": config.placement_param,
            "start": config.start,
        },
        "projection": {"plane": plane, "depth": depth, "overlay": bool(overlay)},
        "metrics": config_dict(),
    }
    if view is not None:
        result["view"] = view
    return result


def _compute_record(requested_backend, *, cpu_forced=False):
    requested = requested_backend or None
    if cpu_forced:
        return {
            "requested_backend": requested,
            "effective_backend": "CPU",
            "result_origin": "computed",
            "producer_backend": "CPU",
            "backend_evidence": "forced_cpu_configuration",
            "fallback_events": [],
        }
    return {
        "requested_backend": requested,
        "effective_backend": None,
        "result_origin": "computed",
        "producer_backend": None,
        "backend_evidence": "not_observed_per_operation",
        "fallback_events": [],
    }


def _write_export_manifest(
    manifest_path,
    experiment_kind,
    outputs,
    *,
    requested_configuration,
    effective_configuration,
    compute,
    randomness=None,
    started_at=None,
    completed_at=None,
    status="completed",
    limitations=None,
    initial_source=None,
    cuda_available=None,
):
    """Write an additive sidecar without changing an existing export."""
    source = collect_source_identity(PROJECT_ROOT, PROVENANCE_SOURCE_FILES)
    if initial_source is not None:
        initial_hashes = {
            item["path"]: item["sha256"] for item in initial_source.get("files", [])
        }
        final_hashes = {item["path"]: item["sha256"] for item in source["files"]}
        source["initial_observation"] = initial_source
        source["changed_since_initial_observation"] = initial_hashes != final_hashes
    else:
        source["changed_since_initial_observation"] = None
    environment = collect_environment(
        cuda_available=cuda_available,
        cupy_relevant=(
            compute.get("effective_backend") == "GPU"
            or str(compute.get("requested_backend")).upper() in ("AUTO", "GPU")
        ),
    )
    manifest = new_experiment_manifest(
        APP_VERSION,
        experiment_kind,
        source=source,
        environment=environment,
        requested_configuration=requested_configuration,
        effective_configuration=effective_configuration,
        randomness=randomness,
        compute=compute,
        started_at=started_at,
        status=status,
        limitations=limitations,
    )
    destination = Path(manifest_path)
    finalized = finalize_experiment_manifest(
        manifest,
        destination.parent,
        outputs,
        manifest_path=destination,
        status=status,
        completed_at=completed_at,
    )
    write_manifest_atomic(destination, finalized)
    return finalized


def colorize(
    values,
    view,
    selected=None,
    edges=None,
    numbers=None,
    mode="Primes",
    param=2,
    overlay=False,
    hits=None,
    visible_depth=1,
):
    values = np.asarray(values, dtype=float)
    if view == "Classic":
        if mode == "Residues modulo N" and numbers is not None:
            palette = np.array(
                [
                    (255, 153, 153),
                    (153, 255, 153),
                    (153, 153, 255),
                    (255, 255, 153),
                    (255, 153, 255),
                    (153, 255, 255),
                    (255, 204, 153),
                    (217, 217, 217),
                    (255, 204, 229),
                    (194, 240, 194),
                ],
                dtype=np.uint8,
            )
            return palette[
                (np.asarray(numbers, dtype=np.int64) % max(1, abs(param)))
                % len(palette)
            ]
        if overlay and hits is not None:
            strength = np.power(
                np.clip(np.asarray(hits, dtype=float) / max(1, visible_depth), 0, 1),
                0.6,
            )
            rgb = np.full((strength.size, 3), 255, dtype=np.uint8)
            rgb[:, 1] = rgb[:, 2] = (255 * (1 - strength)).astype(np.uint8)
            return rgb
        mask = np.asarray(selected if selected is not None else values > 0, dtype=bool)
        rgb = np.full((mask.size, 3), 255, dtype=np.uint8)
        rgb[mask] = (230, 42, 48)
        return rgb
    low = float(np.nanmin(values)) if values.size else 0.0
    high = float(np.nanmax(values)) if values.size else 1.0
    ratio = np.clip((values - low) / max(1e-15, high - low), 0.0, 1.0)
    rgb = np.zeros((values.size, 3), dtype=np.uint8)
    first = ratio < 0.5
    rgb[first, 0] = (ratio[first] * 2 * 255).astype(np.uint8)
    rgb[first, 1] = (ratio[first] * 2 * 255).astype(np.uint8)
    rgb[first, 2] = 255
    rgb[~first, 0] = 255
    rgb[~first, 1] = ((1.0 - ratio[~first]) * 2 * 255).astype(np.uint8)
    if edges is not None:
        rgb[~np.asarray(edges, dtype=bool)] = 255
    return rgb


def colorize_fft(values):
    """Match Matplotlib's v160 FFT rendering (viridis with linear normalization)."""
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values)
    low = float(np.min(values[valid])) if np.any(valid) else 0.0
    high = float(np.max(values[valid])) if np.any(valid) else 1.0
    ratio = np.zeros(values.shape, dtype=float)
    ratio[valid] = np.clip((values[valid] - low) / max(1e-15, high - low), 0.0, 1.0)
    from matplotlib import colormaps

    rgb = (colormaps["viridis"](ratio)[:, :3] * 255).astype(np.uint8)
    rgb[~valid] = (160, 160, 160)
    return rgb


class ImageView(QGraphicsView):
    level_delta = Signal(int)

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self.setMinimumSize(320, 240)
        self.setStyleSheet("background: white; border: 1px solid #bcc3ca;")
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.numbers = None
        self._image_shape = None
        self.show_numbers = True
        self.show_grid = True
        self._grid_item = None
        self._text_items = []

    def set_image(self, image, numbers):
        pixmap = QPixmap.fromImage(image)
        self._item.setPixmap(pixmap)
        self.numbers = np.asarray(numbers)
        self._scene.setSceneRect(QRectF(0, 0, pixmap.width(), pixmap.height()))
        self._rebuild_overlays()
        shape = (pixmap.width(), pixmap.height())
        if shape != self._image_shape:
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._image_shape = shape
        self.viewport().update()

    def set_overlays(self, show_numbers, show_grid):
        self.show_numbers = bool(show_numbers)
        self.show_grid = bool(show_grid)
        if self._grid_item is not None:
            self._grid_item.setVisible(self.show_grid)
        for item in self._text_items:
            item.setVisible(self.show_numbers)
        self.viewport().update()

    def _rebuild_overlays(self):
        if self._grid_item is not None:
            self._scene.removeItem(self._grid_item)
        for item in self._text_items:
            self._scene.removeItem(item)
        self._text_items.clear()
        rows, cols = self.numbers.shape
        path = QPainterPath()
        for x in range(cols + 1):
            path.moveTo(x, 0)
            path.lineTo(x, rows)
        for y in range(rows + 1):
            path.moveTo(0, y)
            path.lineTo(cols, y)
        self._grid_item = QGraphicsPathItem(path)
        pen = QPen(QColor(45, 45, 45, 150))
        pen.setCosmetic(True)
        pen.setWidth(1)
        self._grid_item.setPen(pen)
        self._grid_item.setZValue(1)
        self._grid_item.setVisible(self.show_grid)
        self._scene.addItem(self._grid_item)
        # Individual text items are reliable and sharp for the interactive
        # grid sizes where labels are useful. Avoid tens of thousands of Qt
        # objects for atlas-scale projections.
        if rows * cols <= get_config().max_text_cells:
            font = QFont("Sans Serif")
            font.setPixelSize(12)
            for y in range(rows):
                for x in range(cols):
                    item = QGraphicsSimpleTextItem(str(int(self.numbers[y, x])))
                    item.setFont(font)
                    item.setBrush(QColor(18, 18, 18))
                    item.setZValue(2)
                    bounds = item.boundingRect()
                    scale = min(
                        0.68 / max(1e-9, bounds.width()),
                        0.38 / max(1e-9, bounds.height()),
                    )
                    item.setScale(scale)
                    item.setPos(
                        x + (1 - bounds.width() * scale) / 2,
                        y + (1 - bounds.height() * scale) / 2,
                    )
                    item.setVisible(self.show_numbers)
                    self._scene.addItem(item)
                    self._text_items.append(item)

    def set_error(self, message):
        self._item.setPixmap(QPixmap())
        self.numbers = None
        self._scene.clear()
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self._grid_item = None
        self._text_items.clear()
        text = self._scene.addText(message)
        text.setDefaultTextColor(QColor(120, 20, 20))
        self._scene.setSceneRect(self._scene.itemsBoundingRect())

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.level_delta.emit(1 if event.angleDelta().y() > 0 else -1)
            event.accept()
            return
        factor = 1.22 if event.angleDelta().y() > 0 else 1 / 1.22
        current = self.transform().m11()
        if 0.05 <= current * factor <= 100:
            self.scale(factor, factor)

    def reset_zoom(self):
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class ScanWorker(QObject):
    progress = Signal(int, int)
    backend_status = Signal(str)
    finished = Signal(list)
    failed = Signal(str)

    def __init__(
        self, x1, x2, y1, y2, z, plane, start, trials, backend_mode
    ):
        super().__init__()
        self.args = x1, x2, y1, y2, z, plane, start, trials, backend_mode
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    @Slot()
    def run(self):
        x1, x2, y1, y2, z, plane, start, trials, backend_mode = self.args
        rows = []
        try:
            x_count = abs(int(x2) - int(x1)) + 1
            y_count = abs(int(y2) - int(y1)) + 1
            pair_count = x_count * y_count
            largest_config = GridConfig(
                max(int(x1), int(x2)), max(int(y1), int(y2)), int(z),
                "Primes", 2, "Linear", int(start),
            )
            operation = _overlay_operation_memory_estimate(
                largest_config, plane, trials=int(trials), force_cold=True,
            )
            require_memory(estimate_scan(
                pair_count, result_columns=len(SCAN_COLUMNS),
                operation_peak=operation.additional_peak,
            ))
            pairs = [
                (x, y)
                for y in range(min(y1, y2), max(y1, y2) + 1)
                for x in range(min(x1, x2), max(x1, x2) + 1)
            ]
            self.backend_status.emit(configure_backend(backend_mode))
            clear_volume_cache()
            update_step = max(1, len(pairs) // 200)
            for index, (x, y) in enumerate(pairs, 1):
                if self.cancelled:
                    break
                cfg = GridConfig(x, y, z, "Primes", 2, "Linear", start)
                metrics = overlay_metrics(cfg, plane, random_trials=trials)
                rows.append({"X": x, "Y": y, "Z": z, **metrics})
                # Scan dimensions continually change the FFT shape; old CuPy
                # plans and pooled scratch blocks have little reuse value.
                if index % 128 == 0:
                    release_gpu_caches()
                if index == len(pairs) or index % update_step == 0:
                    self.progress.emit(index, len(pairs))
            rows.sort(key=lambda r: r["structural_score"], reverse=True)
            self.backend_status.emit(backend_summary())
            self.finished.emit(rows)
        except Exception:
            self.failed.emit(traceback.format_exc())
        finally:
            release_gpu_caches()


COMPARISON_METRICS = (
    "alive_density",
    "local_entropy_mean",
    "edge_density",
    "global_entropy",
    "fft_peak_ratio",
    "fft_axis_ratio",
    "fft_lowfreq_ratio",
    "fft_spectral_entropy",
)

COMPARISON_COLUMNS = (
    "placement",
    "classification",
    *COMPARISON_METRICS,
    "distance_from_linear",
)


SCAN_COLUMNS = (
    "X",
    "Y",
    "Z",
    "M",
    "phi_ratio",
    "omega",
    "tau",
    "factorization",
    "alive_density",
    "coprime_alive_ratio",
    "noncoprime_alive_ratio",
    "local_entropy_mean",
    "random_local_entropy_mean",
    "delta_local_entropy_mean",
    "edge_density",
    "random_edge_density",
    "delta_edge_density",
    "global_entropy",
    "random_global_entropy",
    "delta_global_entropy",
    "fft_peak_ratio",
    "random_fft_peak_ratio",
    "delta_fft_peak_ratio",
    "fft_axis_ratio",
    "random_fft_axis_ratio",
    "delta_fft_axis_ratio",
    "fft_lowfreq_ratio",
    "random_fft_lowfreq_ratio",
    "delta_fft_lowfreq_ratio",
    "fft_spectral_entropy",
    "random_fft_spectral_entropy",
    "delta_fft_spectral_entropy",
    "beauty_score",
    "random_beauty_score",
    "structural_score",
    "random_trials",
    "coprime_mask_alive_density",
    "delta_coprime_alive_density",
    "coprime_mask_local_entropy_mean",
    "delta_coprime_local_entropy_mean",
    "coprime_mask_edge_density",
    "delta_coprime_edge_density",
    "coprime_mask_global_entropy",
    "delta_coprime_global_entropy",
    "coprime_mask_fft_peak_ratio",
    "delta_coprime_fft_peak_ratio",
    "coprime_mask_fft_axis_ratio",
    "delta_coprime_fft_axis_ratio",
    "coprime_mask_fft_lowfreq_ratio",
    "delta_coprime_fft_lowfreq_ratio",
    "coprime_mask_fft_spectral_entropy",
    "delta_coprime_fft_spectral_entropy",
    "coprime_residual_l1",
    "coprime_residual_l2",
    "coprime_count",
    "noncoprime_count",
    "coprime_alive_count",
    "noncoprime_alive_count",
)

SCAN_HEATMAP_METRICS = (
    ("Structural score", "structural_score"),
    ("Beauty score", "beauty_score"),
    ("Alive density", "alive_density"),
    ("Coprime alive ratio", "coprime_alive_ratio"),
    ("Non-coprime alive ratio", "noncoprime_alive_ratio"),
    ("Local entropy", "local_entropy_mean"),
    ("Δ local entropy", "delta_local_entropy_mean"),
    ("Edge density", "edge_density"),
    ("Δ edge density", "delta_edge_density"),
    ("Global entropy", "global_entropy"),
    ("Δ global entropy", "delta_global_entropy"),
    ("FFT peak", "fft_peak_ratio"),
    ("Δ FFT peak", "delta_fft_peak_ratio"),
    ("FFT axis", "fft_axis_ratio"),
    ("Δ FFT axis", "delta_fft_axis_ratio"),
    ("FFT low frequency", "fft_lowfreq_ratio"),
    ("Δ FFT low frequency", "delta_fft_lowfreq_ratio"),
    ("FFT spectral entropy", "fft_spectral_entropy"),
    ("Δ FFT spectral entropy", "delta_fft_spectral_entropy"),
    ("Coprime residual L1", "coprime_residual_l1"),
    ("Coprime residual L2", "coprime_residual_l2"),
    ("Δ coprime FFT axis", "delta_coprime_fft_axis_ratio"),
)


class NumericTableItem(QTableWidgetItem):
    def __lt__(self, other):
        left = self.data(Qt.ItemDataRole.UserRole)
        right = other.data(Qt.ItemDataRole.UserRole)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left < right
        return super().__lt__(other)


class PlacementComparisonTab(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.running = False
        self.cancelled = False
        self.rows = []
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.run_button = QPushButton("Compare all placements")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.export_button = QPushButton("Export CSV")
        controls.addWidget(self.run_button)
        controls.addWidget(self.cancel_button)
        controls.addWidget(self.export_button)
        controls.addStretch()
        layout.addLayout(controls)
        self.summary = QLabel(
            "Geometric comparison against Linear; protocol metrics remain Linear-only."
        )
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.table = QTableWidget(0, len(COMPARISON_COLUMNS))
        self.table.setHorizontalHeaderLabels(COMPARISON_COLUMNS)
        self.table.setSortingEnabled(False)
        layout.addWidget(self.table, 1)
        self.run_button.clicked.connect(self.start_comparison)
        self.cancel_button.clicked.connect(self.cancel)
        self.export_button.clicked.connect(self.export_csv)

    def start_comparison(self):
        if self.running:
            return
        config = self.window.config()
        plane = self.window.plane.currentText()
        # Placements run sequentially.  Use the larger placement model once;
        # clearing the LRU is not assumed to release all resident memory.
        try:
            require_memory(_overlay_operation_memory_estimate(
                config, plane, placement="Exploratory placement",
                force_cold=True,
            ))
        except MemoryBudgetExceeded as exc:
            QMessageBox.warning(self, "Memory budget", str(exc))
            return
        self.running = True
        self.cancelled = False
        self.rows = []
        self._configuration = config_dict()
        self._config = self.window.config()
        self._plane = self.window.plane.currentText()
        self._depth = self.window.level.value()
        self._overlay = self.window.overlay.isChecked()
        self._experiment_started_at = utc_now()
        self._initial_source_identity = collect_source_identity(
            PROJECT_ROOT, PROVENANCE_SOURCE_FILES
        )
        self._experiment_completed_at = None
        self._experiment_status = "running"
        self._placement_index = 0
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.window.timer.stop()
        self.window.tabs.widget(0).setEnabled(False)
        self.window.config_tab.setEnabled(False)
        self.progress.setRange(0, len(PLACEMENTS))
        self.progress.setValue(0)
        configure_backend("CPU")
        self._backend_state = backend_state()
        QTimer.singleShot(0, self._run_next)

    def _run_next(self):
        if self.cancelled or self._placement_index >= len(PLACEMENTS):
            self._complete_run()
            return
        placement = PLACEMENTS[self._placement_index]
        try:
            cfg = GridConfig(
                self._config.x,
                self._config.y,
                self._config.z,
                self._config.mode,
                self._config.param,
                placement,
                self._config.start,
                self._config.placement_param,
            )
            clear_volume_cache()
            metrics = placement_geometry_metrics(
                cfg, self._plane, self._depth, self._overlay
            )
            self.rows.append(
                {
                    "placement": placement,
                    "classification": (
                        "Protocol-valid" if placement == "Linear" else "Exploratory"
                    ),
                    **metrics,
                }
            )
            self._placement_index += 1
            self.progress.setValue(self._placement_index)
            QTimer.singleShot(0, self._run_next)
        except Exception:
            QMessageBox.critical(
                self, "Placement comparison", traceback.format_exc()
            )
            self.cancelled = True
            self._experiment_status = "failed"
            self._complete_run()

    def _complete_run(self):
        linear = next(
            (row for row in self.rows if row["placement"] == "Linear"), None
        )
        for row in self.rows:
            row["distance_from_linear"] = (
                float(
                    np.sqrt(
                        sum(
                            (row[key] - linear[key]) ** 2
                            for key in COMPARISON_METRICS
                        )
                    )
                )
                if linear is not None
                else float("nan")
            )
        self.comparison_finished(self.rows)
        if self._experiment_status != "failed":
            self._experiment_status = "cancelled" if self.cancelled else "completed"
        self._experiment_completed_at = utc_now()
        clear_volume_cache()
        self.running = False
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.window.tabs.widget(0).setEnabled(True)
        self.window.config_tab.setEnabled(True)
        self.window.backend_changed()

    @Slot(list)
    def comparison_finished(self, rows):
        self.rows = rows
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, key in enumerate(COMPARISON_COLUMNS):
                value = row.get(key, "")
                text = f"{value:.6g}" if isinstance(value, float) else str(value)
                item = QTableWidgetItem(text)
                if isinstance(value, (int, float)):
                    item.setData(Qt.ItemDataRole.UserRole, value)
                self.table.setItem(row_index, column_index, item)
        self.table.resizeColumnsToContents()
        linear = next((row for row in rows if row["placement"] == "Linear"), None)
        if linear:
            self.summary.setText(
                f"Linear reference — FFT peak {linear['fft_peak_ratio']:.4f}, "
                f"axis {linear['fft_axis_ratio']:.4f}, local entropy "
                f"{linear['local_entropy_mean']:.4f}."
            )

    def cancel(self):
        self.cancelled = True

    def export_csv(self):
        if not self.rows:
            QMessageBox.information(self, "Placement comparison", "Run a comparison first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export placement comparison", "placement_comparison.csv", "CSV (*.csv)"
        )
        if not path:
            return
        output_path = Path(path)
        config_path = output_path.with_suffix(".config.json")
        manifest_path = manifest_sidecar_path(output_path)
        with ExportConsistencyGuard(manifest_path, [output_path, config_path]):
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=COMPARISON_COLUMNS, delimiter=";")
                writer.writeheader()
                writer.writerows(self.rows)
            metadata = {
                "application_version": APP_VERSION,
                "comparison_reference": "Linear",
                "grid": {
                    "x": self._config.x,
                    "y": self._config.y,
                    "z": self._config.z,
                    "mode": self._config.mode,
                    "mode_parameter": self._config.param,
                    "placement_parameter": self._config.placement_param,
                    "start": self._config.start,
                    "plane": self._plane,
                    "depth": self._depth,
                    "overlay": self._overlay,
                },
                "metrics": list(COMPARISON_METRICS),
                "configuration": self._configuration,
                "backend": self._backend_state,
            }
            config_path.write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            requested = _grid_configuration(
                self._config, self._plane, self._depth, self._overlay
            )
            requested["comparison_reference"] = "Linear"
            requested["comparison_metrics"] = list(COMPARISON_METRICS)
            result_status = (
                "partial" if self._experiment_status in ("cancelled", "failed")
                else "complete"
            )
            _write_export_manifest(
                manifest_path,
                "placement_comparison",
                [
                    {
                        "path": output_path.name,
                        "status": result_status,
                        "scientific_completeness": result_status,
                    },
                    {
                        "path": config_path.name,
                        "scientific_completeness": "not_applicable",
                    },
                ],
                requested_configuration=requested,
                effective_configuration=requested,
                compute=_compute_record("CPU", cpu_forced=True),
                started_at=self._experiment_started_at,
                completed_at=self._experiment_completed_at,
                status=self._experiment_status,
                limitations=[
                    "The manifest is persisted at export time; no destination existed when the comparison started."
                ],
                initial_source=self._initial_source_identity,
                cuda_available=self._backend_state["cuda_available"],
            )

    def stop(self):
        if self.running:
            self.cancelled = True
            self.running = False
        return True


class ConfigurationTab(QWidget):
    applied = Signal(object)

    INTEGER_FIELDS = (
        ("gpu_auto_min_elements", "Auto GPU threshold", 1, 1_000_000_000),
        ("max_volume", "Maximum volume", 1, 1_000_000_000),
        ("baseline_trials", "Default baseline trials", 1, 100_000),
        ("baseline_seed", "Baseline seed (-1=derived)", -1, 2_147_483_647),
        ("entropy_bins", "Local entropy bins", 2, 256),
        ("max_text_cells", "Maximum text labels", 0, 1_000_000),
        ("max_3d_points", "Maximum 3D points", 1, 100_000_000),
        ("redraw_delay_ms", "Redraw debounce (ms)", 0, 5_000),
        ("export_max_side", "Batch export max side", 64, 32_768),
    )
    FLOAT_FIELDS = (
        ("edge_threshold", "Entropy edge threshold", 0.0, 1.0, 3),
        ("fft_low_radius", "FFT low-frequency radius", 0.001, 1.0, 3),
        ("beauty_entropy_weight", "Beauty entropy weight", 0.0, 10.0, 3),
        ("beauty_edge_weight", "Beauty edge weight", 0.0, 10.0, 3),
        ("beauty_target_density", "Beauty target density", 0.0, 1.0, 3),
        ("beauty_density_decay", "Beauty density decay", 0.0, 1_000.0, 3),
        ("point_size_3d", "3D point size", 0.1, 100.0, 1),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        notice = QLabel(
            "Scientific parameters affect metrics and must be saved with every experiment. "
            "Defaults preserve the validated v170 numerical behavior."
        )
        notice.setWordWrap(True)
        root.addWidget(notice)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll, 1)
        body = QWidget()
        scroll.setWidget(body)
        layout = QFormLayout(body)
        self.controls = {}
        for name, label, low, high in self.INTEGER_FIELDS:
            widget = QSpinBox()
            widget.setRange(low, high)
            widget.setGroupSeparatorShown(True)
            self.controls[name] = widget
            layout.addRow(label, widget)
        for name, label, low, high, decimals in self.FLOAT_FIELDS:
            widget = QDoubleSpinBox()
            widget.setRange(low, high)
            widget.setDecimals(decimals)
            widget.setSingleStep(0.01)
            self.controls[name] = widget
            layout.addRow(label, widget)
        buttons = QHBoxLayout()
        root.addLayout(buttons)
        for label, callback in (
            ("Apply", self.apply),
            ("Reset defaults", self.reset),
            ("Load JSON", self.load),
            ("Save JSON", self.save),
        ):
            button = QPushButton(label)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        self.status = QLabel()
        root.addWidget(self.status)
        self.set_values(get_config())

    def set_values(self, config):
        for name, widget in self.controls.items():
            widget.setValue(getattr(config, name))

    def values(self):
        values = config_dict()
        for name, widget in self.controls.items():
            values[name] = widget.value()
        return AppConfig(**values)

    def apply(self):
        config = set_config(self.values())
        self.set_values(config)
        self.status.setText("Configuration applied (not yet saved).")
        self.applied.emit(config)

    def reset(self):
        config = reset_config()
        self.set_values(config)
        self.status.setText("Defaults restored.")
        self.applied.emit(config)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load configuration", "", "JSON (*.json)"
        )
        if path:
            try:
                config = load_config(path)
                self.set_values(config)
                self.status.setText(f"Loaded: {path}")
                self.applied.emit(config)
            except Exception as exc:
                QMessageBox.critical(self, "Configuration error", str(exc))

    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save configuration", "prime_atlas_config.json", "JSON (*.json)"
        )
        if path:
            try:
                config = set_config(self.values())
                save_config(path, config)
                self.set_values(config)
                self.status.setText(f"Saved: {path}")
                self.applied.emit(config)
            except Exception as exc:
                QMessageBox.critical(self, "Configuration error", str(exc))


class ModuleScanTab(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.rows = []
        self.scan_metadata = None
        self.thread = None
        self.worker = None
        layout = QVBoxLayout(self)
        inputs = QHBoxLayout()
        self.x1 = self.spin(window.x_spin.value(), 1, 9999)
        self.x2 = self.spin(window.x_spin.value() + 10, 1, 9999)
        self.y1 = self.spin(window.y_spin.value(), 1, 9999)
        self.y2 = self.spin(window.y_spin.value() + 10, 1, 9999)
        self.z = self.spin(window.z_spin.value(), 1, 9999)
        self.trials = self.spin(get_config().baseline_trials, 1, 1000)
        for label, widget in (
            ("X from", self.x1),
            ("to", self.x2),
            ("Y from", self.y1),
            ("to", self.y2),
            ("Z", self.z),
            ("Trials", self.trials),
        ):
            inputs.addWidget(QLabel(label))
            inputs.addWidget(widget)
        inputs.addWidget(QLabel("Compute"))
        self.backend = QComboBox()
        self.backend.addItems(("Auto", "CPU", "GPU"))
        self.backend.setCurrentText(window.backend.currentText())
        inputs.addWidget(self.backend)
        self.run_button = QPushButton("Run")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        export = QPushButton("Export CSV")
        inputs.addWidget(self.run_button)
        inputs.addWidget(self.cancel_button)
        inputs.addWidget(export)
        layout.addLayout(inputs)
        self.backend_status = QLabel(
            "Scan metrics use the selected NumPy/CuPy backend."
        )
        layout.addWidget(self.backend_status)
        self.cost_label = QLabel()
        layout.addWidget(self.cost_label)
        tools = QHBoxLayout()
        tools.addWidget(QLabel("Heatmap metric"))
        self.heatmap_metric = QComboBox()
        for label, metric in SCAN_HEATMAP_METRICS:
            self.heatmap_metric.addItem(label, metric)
        tools.addWidget(self.heatmap_metric, 1)
        show_heatmap = QPushButton("Show heatmap")
        show_heatmap.clicked.connect(self.show_selected_heatmap)
        tools.addWidget(show_heatmap)
        save_screenshot = QPushButton("Save screenshot")
        save_screenshot.clicked.connect(self.save_selected_screenshot)
        tools.addWidget(save_screenshot)
        batch = QPushButton("Save all metric screenshots")
        batch.clicked.connect(self.save_all_metric_screenshots)
        tools.addWidget(batch)
        layout.addLayout(tools)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.table = QTableWidget(0, len(SCAN_COLUMNS))
        self.table.setHorizontalHeaderLabels(SCAN_COLUMNS)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        self.run_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.cancel_scan)
        export.clicked.connect(self.export_csv)
        for widget in (self.x1, self.x2, self.y1, self.y2, self.trials):
            widget.valueChanged.connect(self.update_cost_label)
        self.backend.currentTextChanged.connect(self.update_cost_label)
        self.update_cost_label()

    @staticmethod
    def spin(value, low, high):
        widget = QSpinBox()
        widget.setRange(low, high)
        widget.setValue(value)
        return widget

    def start_scan(self):
        count = (abs(self.x2.value() - self.x1.value()) + 1) * (
            abs(self.y2.value() - self.y1.value()) + 1
        )
        max_x = max(self.x1.value(), self.x2.value())
        max_y = max(self.y1.value(), self.y2.value())
        largest_config = GridConfig(
            max_x, max_y, self.z.value(), "Primes", 2, "Linear",
            self.window.start_spin.value(),
        )
        operation = _overlay_operation_memory_estimate(
            largest_config, self.window.plane.currentText(),
            trials=self.trials.value(), force_cold=True,
        )
        try:
            require_memory(estimate_scan(
                count, result_columns=len(SCAN_COLUMNS),
                operation_peak=operation.additional_peak,
            ))
        except MemoryBudgetExceeded as exc:
            QMessageBox.warning(self, "Memory budget", str(exc))
            return
        self.update_cost_label()
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.window.config_tab.setEnabled(False)
        self.window.timer.stop()
        self.window.tabs.widget(0).setEnabled(False)
        self.progress.setRange(0, count)
        self.progress.setValue(0)
        # Bind exported provenance to this run, not to later edits in the UI.
        self.rows = []
        self.table.setRowCount(0)
        self.scan_metadata = config_dict()
        self.scan_metadata["application_version"] = APP_VERSION
        self.scan_metadata["_scan"] = {
            "x_from": self.x1.value(), "x_to": self.x2.value(),
            "y_from": self.y1.value(), "y_to": self.y2.value(),
            "z": self.z.value(), "trials": self.trials.value(),
            "compute": self.backend.currentText(),
            "plane": self.window.plane.currentText(),
            "placement": "Linear", "mode": "Primes",
            "start": self.window.start_spin.value(), "overlay": True,
            "depth": "full", "status": "running",
        }
        self._experiment_started_at = utc_now()
        self._initial_source_identity = collect_source_identity(
            PROJECT_ROOT, PROVENANCE_SOURCE_FILES
        )
        self._experiment_completed_at = None
        self._experiment_status = "running"
        self.thread = QThread(self)
        self.worker = ScanWorker(
            self.x1.value(),
            self.x2.value(),
            self.y1.value(),
            self.y2.value(),
            self.z.value(),
            self.window.plane.currentText(),
            self.window.start_spin.value(),
            self.trials.value(),
            self.backend.currentText(),
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(
            self.scan_progress, Qt.ConnectionType.QueuedConnection
        )
        self.worker.backend_status.connect(self.scan_backend_status)
        self.worker.finished.connect(self.scan_finished)
        self.worker.failed.connect(self.scan_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.thread_finished)
        self.thread.start()

    @Slot()
    def update_cost_label(self):
        combinations = (abs(self.x2.value() - self.x1.value()) + 1) * (
            abs(self.y2.value() - self.y1.value()) + 1
        )
        passes = combinations * (self.trials.value() + 2)
        note = ""
        if self.backend.currentText() == "GPU":
            note = " — forced GPU may be slower for small planes; Auto is recommended"
        self.cost_label.setText(
            f"Cost: {combinations:,} combinations × "
            f"{self.trials.value() + 2} metric passes = {passes:,}{note}"
        )

    @Slot(int, int)
    def scan_progress(self, done, total):
        if self.progress.maximum() != total:
            self.progress.setMaximum(total)
        self.progress.setValue(done)

    @Slot(str)
    def scan_backend_status(self, status):
        self.backend_status.setText(status)
        if hasattr(self, "scan_metadata"):
            self.scan_metadata["_scan"]["backend_runtime_policy"] = status

    def thread_finished(self):
        self.worker = None
        self.thread = None
        self.window.config_tab.setEnabled(True)
        self.window.tabs.widget(0).setEnabled(True)
        self.window.backend_changed()

    def cancel_scan(self):
        if self.worker:
            self.worker.cancel()

    @Slot(list)
    def scan_finished(self, rows):
        self._experiment_status = (
            "cancelled" if self.worker and self.worker.cancelled else "completed"
        )
        self._experiment_completed_at = utc_now()
        self.scan_metadata["_scan"]["status"] = self._experiment_status
        self.rows = rows
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                for col_index, key in enumerate(SCAN_COLUMNS):
                    value = row.get(key, "")
                    text = f"{value:.6g}" if isinstance(value, float) else str(value)
                    item = NumericTableItem(text)
                    if isinstance(value, (int, float)):
                        item.setData(Qt.ItemDataRole.UserRole, value)
                    self.table.setItem(row_index, col_index, item)
            self.table.setSortingEnabled(True)
            self.table.resizeColumnsToContents()
        finally:
            self.table.setUpdatesEnabled(True)
            self.table.viewport().update()
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    @Slot(str)
    def scan_failed(self, error):
        self._experiment_status = "failed"
        self._experiment_completed_at = utc_now()
        self.scan_metadata["_scan"]["status"] = "failed"
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.critical(self, "Scan error", error)

    def export_csv(self):
        if not self.rows:
            QMessageBox.information(self, "Export", "Run a scan first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export scan", "atlas.csv", "CSV (*.csv)"
        )
        if path:
            output_path = Path(path)
            sidecar = output_path.with_suffix(".config.json")
            manifest_path = manifest_sidecar_path(output_path)
            with ExportConsistencyGuard(manifest_path, [output_path, sidecar]):
                with open(path, "w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(
                        handle,
                        fieldnames=SCAN_COLUMNS,
                        delimiter=";",
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    writer.writerows(self.rows)
                metadata = self.scan_metadata
                sidecar.write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
                scan = metadata["_scan"]
                requested = {
                    "scan": {
                        key: value for key, value in scan.items()
                        if key not in ("status", "backend_runtime_policy")
                    },
                    "metrics": {
                        key: value for key, value in metadata.items()
                        if key not in ("_scan", "application_version")
                    },
                }
                seed = requested["metrics"].get("baseline_seed")
                randomness = {
                    "status": "observed_configuration",
                    "seed": seed if isinstance(seed, int) and seed >= 0 else None,
                    "seed_status": "explicit" if isinstance(seed, int) and seed >= 0 else "derived_per_grid",
                    "algorithm": "numpy.random.default_rng",
                    "algorithm_status": "constructor_observed_in_implementation",
                    "trials": scan["trials"],
                    "universal_reproducibility_guaranteed": False,
                }
                result_status = (
                    "partial" if self._experiment_status in ("cancelled", "failed")
                    else "complete"
                )
                _write_export_manifest(
                    manifest_path,
                    "module_scan",
                    [
                        {
                            "path": output_path.name,
                            "status": result_status,
                            "scientific_completeness": result_status,
                        },
                        {
                            "path": sidecar.name,
                            "scientific_completeness": "not_applicable",
                        },
                    ],
                    requested_configuration=requested,
                    effective_configuration=requested,
                    compute=_compute_record(
                        scan["compute"], cpu_forced=scan["compute"] == "CPU"
                    ),
                    randomness=randomness,
                    started_at=self._experiment_started_at,
                    completed_at=self._experiment_completed_at,
                    status=self._experiment_status,
                    limitations=[
                        "Backend execution is not instrumented per operation; non-CPU producer backend remains unverified.",
                        "The manifest is persisted at export time; no destination existed when the scan started.",
                    ],
                    initial_source=self._initial_source_identity,
                )
            QMessageBox.information(
                self, "Export", f"Saved CSV and configuration:\n{sidecar}"
            )

    def heatmap_matrix(self, metric):
        xs = sorted({int(row["X"]) for row in self.rows})
        ys = sorted({int(row["Y"]) for row in self.rows})
        x_index = {value: i for i, value in enumerate(xs)}
        y_index = {value: i for i, value in enumerate(ys)}
        matrix = np.full((len(ys), len(xs)), np.nan)
        for row in self.rows:
            matrix[y_index[int(row["Y"])], x_index[int(row["X"])]] = float(
                row.get(metric, np.nan)
            )
        return xs, ys, matrix

    def save_heatmap_figure(self, metric, label, path):
        import matplotlib.pyplot as plt

        xs, ys, matrix = self.heatmap_matrix(metric)
        fig, ax = plt.subplots(figsize=(10, 8))
        image = ax.imshow(
            matrix,
            origin="lower",
            aspect="auto",
            cmap="viridis",
            extent=(xs[0] - 0.5, xs[-1] + 0.5, ys[0] - 0.5, ys[-1] + 0.5),
        )
        ax.set(title=label, xlabel="X", ylabel="Y")
        fig.colorbar(image, ax=ax, label=label)
        fig.tight_layout()
        fig.savefig(path, dpi=180)
        plt.close(fig)

    def show_heatmap(self, metric, save=False):
        if not self.rows:
            QMessageBox.information(self, "Heatmap", "Run a scan first.")
            return
        label = self.heatmap_metric.currentText()
        if save:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save scan screenshot", f"{metric}.png", "PNG (*.png)"
            )
            if path:
                output_path = Path(path)
                manifest_path = manifest_sidecar_path(output_path)
                with ExportConsistencyGuard(manifest_path, [output_path]):
                    self.save_heatmap_figure(metric, label, path)
                    scan = self.scan_metadata["_scan"]
                    configuration = {
                        "scan": {
                            key: value for key, value in scan.items()
                            if key != "backend_runtime_policy"
                        },
                        "metric": metric,
                        "label": label,
                    }
                    scientific_status = (
                        "partial" if self._experiment_status in ("cancelled", "failed")
                        else "complete"
                    )
                    _write_export_manifest(
                        manifest_path,
                        "scan_metric_screenshot",
                        [{
                            "path": output_path.name,
                            "status": scientific_status,
                            "scientific_completeness": scientific_status,
                        }],
                        requested_configuration=configuration,
                        effective_configuration=configuration,
                        compute=_compute_record(
                            scan["compute"], cpu_forced=scan["compute"] == "CPU"
                        ),
                        started_at=self._experiment_started_at,
                        completed_at=self._experiment_completed_at,
                        status=self._experiment_status,
                        limitations=["The image sidecar is created only after an export destination is selected."],
                        initial_source=self._initial_source_identity,
                    )
        else:
            _, _, matrix = self.heatmap_matrix(metric)
            self.window.show_matrix_tab(matrix, metric)

    def show_selected_heatmap(self):
        self.show_heatmap(self.heatmap_metric.currentData())

    def save_selected_screenshot(self):
        self.show_heatmap(self.heatmap_metric.currentData(), save=True)

    def save_all_metric_screenshots(self):
        if not self.rows:
            QMessageBox.information(self, "Metric screenshots", "Run a scan first.")
            return
        directory = QFileDialog.getExistingDirectory(
            self, "Select directory for all metric screenshots"
        )
        if not directory:
            return
        output = Path(directory)
        manifest = []
        metadata_path = output / "metric_screenshots.json"
        manifest_path = manifest_sidecar_path(metadata_path)
        batch_paths = [
            output / f"{index:02d}_{metric}.png"
            for index, (_, metric) in enumerate(SCAN_HEATMAP_METRICS, 1)
        ] + [metadata_path]
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            with ExportConsistencyGuard(manifest_path, batch_paths):
                for index, (label, metric) in enumerate(SCAN_HEATMAP_METRICS, 1):
                    filename = f"{index:02d}_{metric}.png"
                    self.save_heatmap_figure(metric, label, output / filename)
                    manifest.append(
                        {"index": index, "label": label, "metric": metric, "file": filename}
                    )
                    QApplication.processEvents()
                metadata = {
                    "application_version": APP_VERSION,
                    "screenshots": manifest,
                    "scan": dict(self.scan_metadata["_scan"]),
                    "configuration": {
                        key: value for key, value in self.scan_metadata.items()
                        if key not in ("_scan", "application_version")
                    },
                }
                metadata_path.write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                scan = self.scan_metadata["_scan"]
                requested = {
                    "scan": {
                        key: value for key, value in scan.items()
                        if key != "backend_runtime_policy"
                    },
                    "metrics": [item["metric"] for item in manifest],
                }
                scientific_status = (
                    "partial" if self._experiment_status in ("cancelled", "failed")
                    else "complete"
                )
                outputs = [
                    {
                        "path": item["file"],
                        "status": scientific_status,
                        "scientific_completeness": scientific_status,
                    }
                    for item in manifest
                ]
                outputs.append({
                    "path": metadata_path.name,
                    "scientific_completeness": "not_applicable",
                })
                _write_export_manifest(
                    manifest_path,
                    "scan_metric_screenshot_batch",
                    outputs,
                    requested_configuration=requested,
                    effective_configuration=requested,
                    compute=_compute_record(
                        scan["compute"], cpu_forced=scan["compute"] == "CPU"
                    ),
                    started_at=self._experiment_started_at,
                    completed_at=self._experiment_completed_at,
                    status=self._experiment_status,
                    limitations=["The batch sidecar is created only after an export directory is selected."],
                    initial_source=self._initial_source_identity,
                )
        except Exception as exc:
            QMessageBox.critical(self, "Metric screenshots", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        QMessageBox.information(
            self,
            "Metric screenshots",
            f"Saved {len(manifest)} metric screenshots in:\n{output}",
        )

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.worker.cancel()
            self.thread.quit()
            if not self.thread.wait(5000):
                event.ignore()
                return
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Prime Grid Atlas v{APP_VERSION}")
        self.resize(1500, 900)
        self.current_image = None
        self.current_data = None
        self.gl_dialog = None
        self.gl_view = None
        self.gl_items = []
        self._gl_center = QVector3D(0, 0, 0)
        self._gl_distance = 10.0
        self._gl_pan_step = 1.0
        self._gl_outer_radius = 1.0
        self._gl_is_spherical = False
        self.scan_tab = None
        self.comparison_tab = None
        self.analysis_tab = None
        self.analysis_view = None
        self.analysis_title = None
        self._ratio_guard = False
        self._application_source_identity = collect_source_identity(
            PROJECT_ROOT, PROVENANCE_SOURCE_FILES
        )
        self._locked_dims = (10, 10, 10)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.render)
        self._build_ui()
        self.backend_changed()
        self.schedule_render()

    def _build_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)
        grid_page = QWidget()
        grid_page_layout = QVBoxLayout(grid_page)
        grid_page_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter()
        grid_page_layout.addWidget(splitter)
        self.tabs.addTab(grid_page, "Grid")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(330)
        scroll.setMaximumWidth(470)
        controls = QWidget()
        side = QVBoxLayout(controls)
        scroll.setWidget(controls)
        splitter.addWidget(scroll)
        self.image_view = ImageView()
        splitter.addWidget(self.image_view)
        splitter.setStretchFactor(1, 1)

        dimensions = QGroupBox("Dimensions")
        grid = QGridLayout(dimensions)
        self.x_spin = self.spin(10, 1, 9999)
        self.y_spin = self.spin(10, 1, 9999)
        self.z_spin = self.spin(10, 1, 9999)
        for col, (label, widget) in enumerate(
            (("X", self.x_spin), ("Y", self.y_spin), ("Z", self.z_spin))
        ):
            grid.addWidget(QLabel(label), 0, col * 2)
            grid.addWidget(widget, 0, col * 2 + 1)
        self.lock_ratio = QCheckBox("Lock aspect ratio")
        self.lock_ratio.toggled.connect(self.lock_ratio_changed)
        grid.addWidget(self.lock_ratio, 1, 0, 1, 3)
        draw = QPushButton("Draw")
        draw.clicked.connect(self.render)
        grid.addWidget(draw, 1, 3, 1, 3)
        side.addWidget(dimensions)

        presets = QGroupBox("Quick presets")
        pg = QGridLayout(presets)
        preset_data = (
            ("Linear 71×30×30", (71, 30, 30, "Primes", True, "Classic")),
            ("37×32×30", (37, 32, 30, None, None, None)),
            ("Prime overlay", (30, 30, 12, "Primes", True, "Classic")),
            ("Entropy", (40, 40, 8, "Primes", True, "Local entropy")),
            ("Twin primes", (30, 30, 12, "Twin primes", True, "Classic")),
            ("Residues mod N", (30, 30, 3, "Residues modulo N", False, "Classic")),
        )
        for i, (text, args) in enumerate(preset_data):
            button = QPushButton(text)
            button.clicked.connect(lambda checked=False, a=args: self.apply_preset(*a))
            pg.addWidget(button, i // 2, i % 2)
        side.addWidget(presets)

        analysis = QGroupBox("Numerical analysis")
        form = QFormLayout(analysis)
        self.backend = QComboBox()
        self.backend.addItems(("Auto", "CPU", "GPU"))
        self.backend.currentTextChanged.connect(self.backend_changed)
        self.backend_label = QLabel()
        self.backend_label.setWordWrap(True)
        form.addRow("Compute", self.backend)
        form.addRow(self.backend_label)
        gpu_help = QPushButton("GPU diagnostics / setup")
        gpu_help.clicked.connect(self.show_gpu_diagnostics)
        form.addRow(gpu_help)
        self.overlay = QCheckBox("Accumulate 0..k on orthogonal axis")
        form.addRow(self.overlay)
        self.start_spin = self.spin(1, -999999, 999999)
        form.addRow("Start", self.start_spin)
        self.mode_family = QComboBox()
        self.mode_family.addItems(MODE_GROUPS)
        form.addRow("Mode group", self.mode_family)
        self.mode = QComboBox()
        self.mode.addItems(PRIME_MODES)
        form.addRow("Mode", self.mode)
        self.mode_help = QLabel("Prime masks and prime constellations")
        self.mode_help.setWordWrap(True)
        form.addRow(self.mode_help)
        self.param = self.spin(2, -999999, 999999)
        self.parameter_label = QLabel("Parameter")
        form.addRow(self.parameter_label, self.param)
        self.placement = QComboBox()
        self.placement.addItems(PLACEMENTS)
        form.addRow("Placement", self.placement)
        self.placement_param = self.spin(7, -999999, 999999)
        self.placement_param.setEnabled(False)
        form.addRow("Placement parameter / seed", self.placement_param)
        self.placement_help = QLabel("Scientific reference embedding")
        self.placement_help.setWordWrap(True)
        form.addRow(self.placement_help)
        side.addWidget(analysis)

        view = QGroupBox("View")
        vf = QFormLayout(view)
        self.view_mode = QComboBox()
        self.view_mode.addItems(
            (
                "Classic",
                "Heatmap",
                "Normalized heatmap",
                "Gradient",
                "Local entropy",
                "Entropy edges only",
                "FFT 2D",
            )
        )
        vf.addRow("View type", self.view_mode)
        self.plane = QComboBox()
        self.plane.addItems(("XY", "XZ", "YZ"))
        vf.addRow("Plane", self.plane)
        overlay_options = QHBoxLayout()
        self.show_numbers = QCheckBox("Numbers")
        self.show_numbers.setChecked(True)
        self.show_grid = QCheckBox("Grid")
        self.show_grid.setChecked(True)
        overlay_options.addWidget(self.show_numbers)
        overlay_options.addWidget(self.show_grid)
        vf.addRow(overlay_options)
        self.selected_only_3d = QCheckBox("3D selected only")
        self.selected_only_3d.setChecked(True)
        vf.addRow(self.selected_only_3d)
        self.geometry_3d = QComboBox()
        self.geometry_3d.addItems(
            ("Cartesian grid", "Spherical shells", "Rotating spherical shells")
        )
        vf.addRow("3D geometry", self.geometry_3d)
        self.shell_inner_radius = QDoubleSpinBox()
        self.shell_inner_radius.setRange(0.1, 10_000.0)
        self.shell_inner_radius.setValue(8.0)
        self.shell_inner_radius.setDecimals(2)
        vf.addRow("Inner shell radius", self.shell_inner_radius)
        self.shell_spacing = QDoubleSpinBox()
        self.shell_spacing.setRange(0.01, 1_000.0)
        self.shell_spacing.setValue(1.0)
        self.shell_spacing.setDecimals(2)
        vf.addRow("Shell spacing", self.shell_spacing)
        self.shell_rotation = QDoubleSpinBox()
        self.shell_rotation.setRange(-360.0, 360.0)
        self.shell_rotation.setValue(12.0)
        self.shell_rotation.setSuffix("° / level")
        self.shell_rotation.setDecimals(2)
        vf.addRow("Shell rotation", self.shell_rotation)
        self.geometry_3d.currentTextChanged.connect(self.geometry_3d_changed)
        self.geometry_3d_changed(self.geometry_3d.currentText())
        level_row = QHBoxLayout()
        level_down = QPushButton("<")
        level_up = QPushButton(">")
        self.level = QSlider(Qt.Orientation.Horizontal)
        self.level.setRange(0, 9)
        self.level_value = QLabel("1/10")
        level_down.clicked.connect(lambda: self.adjust_level(-1))
        level_up.clicked.connect(lambda: self.adjust_level(1))
        level_row.addWidget(level_down)
        level_row.addWidget(self.level, 1)
        level_row.addWidget(level_up)
        level_row.addWidget(self.level_value)
        vf.addRow("Level", level_row)
        vf.addRow(QLabel("Wheel: zoom | Shift+wheel: level"))
        side.addWidget(view)

        actions = QGroupBox("Actions")
        ag = QGridLayout(actions)
        for index, (text, slot) in enumerate(
            (
                ("Reset view", self.image_view.reset_zoom),
                ("3D view", self.show_3d),
                ("Save PNG", self.save_png),
                ("Module scan", self.open_scan),
                ("FFT 2D", self.show_fft),
                ("Save FFT", self.save_fft),
                ("Compare placements", self.open_placement_comparison),
            )
        ):
            button = QPushButton(text)
            button.clicked.connect(slot)
            ag.addWidget(button, index // 2, index % 2)
        side.addWidget(actions)
        side.addStretch()
        self.setStatusBar(QStatusBar())

        self.x_spin.valueChanged.connect(lambda: self.dimension_changed("x"))
        self.y_spin.valueChanged.connect(lambda: self.dimension_changed("y"))
        self.z_spin.valueChanged.connect(lambda: self.dimension_changed("z"))
        for widget in (self.start_spin, self.param, self.placement_param):
            widget.valueChanged.connect(self.schedule_render)
        self.mode_family.currentTextChanged.connect(self.mode_family_changed)
        self.mode.currentTextChanged.connect(self.mode_changed)
        self.placement.currentTextChanged.connect(self.placement_changed)
        self.view_mode.currentTextChanged.connect(self.schedule_render)
        self.overlay.toggled.connect(self.schedule_render)
        self.level.valueChanged.connect(self.schedule_render)
        self.level.valueChanged.connect(
            lambda value: self.level_value.setText(
                f"{value + 1}/{self.level.maximum() + 1}"
            )
        )
        self.show_numbers.toggled.connect(self.overlay_options_changed)
        self.show_grid.toggled.connect(self.overlay_options_changed)
        self.plane.currentTextChanged.connect(self.plane_changed)
        self.image_view.level_delta.connect(self.adjust_level)
        self.mode_changed(self.mode.currentText())

        self.config_tab = ConfigurationTab(self)
        self.config_tab.applied.connect(self.apply_app_config)
        self.tabs.addTab(self.config_tab, "Configuration")

    @staticmethod
    def spin(value, low, high):
        widget = QSpinBox()
        widget.setRange(low, high)
        widget.setValue(value)
        return widget

    def config(self):
        return GridConfig(
            self.x_spin.value(),
            self.y_spin.value(),
            self.z_spin.value(),
            self.mode.currentText(),
            self.param.value(),
            self.placement.currentText(),
            self.start_spin.value(),
            self.placement_param.value(),
        )

    def geometry_3d_changed(self, geometry):
        spherical = geometry != "Cartesian grid"
        self.shell_inner_radius.setEnabled(spherical)
        self.shell_spacing.setEnabled(spherical)
        self.shell_rotation.setEnabled(geometry == "Rotating spherical shells")

    def placement_changed(self, placement):
        uses_parameter = placement in ("Prime modulus weave", "Seeded random")
        self.placement_param.setEnabled(uses_parameter)
        descriptions = {
            "Linear": "Scientific reference embedding",
            "Spiral inward": "Clockwise from the outer border to the center",
            "Spiral outward (Ulam)": "Classic center-out prime spiral",
            "Boustrophedon": "Alternating left-to-right and right-to-left rows",
            "Hilbert curve": "Fractal traversal preserving spatial locality",
            "Morton Z-order": "Recursive blocks ordered by interleaved coordinate bits",
            "Diagonal zigzag": "Alternating diagonal traversal",
            "Corner expanding rings": "Growing shells from the top-left corner",
            "Concentric rings": "Outside-in rings with alternating direction",
            "Radial spokes": "Center-out traversal grouped by angular ray",
            "Prime modulus weave": "Groups values by n mod placement parameter",
            "Seeded random": "Reproducible random permutation using the placement seed",
            "Bit reversal": "Hierarchy generated by reversed index bits",
            "3D helix": "Rotates the inward spiral between Z levels",
        }
        self.placement_help.setText(descriptions.get(placement, ""))
        self.schedule_render()

    def mode_changed(self, mode):
        uses_parameter = mode in (
            "Multiples of k",
            "Residues modulo N",
            "Coprimes with N",
            "GCD with N",
        )
        self.param.setEnabled(uses_parameter)
        self.parameter_label.setText("Parameter")
        self.schedule_render()

    def mode_family_changed(self, family):
        previous = self.mode.currentText()
        choices = MODE_GROUPS.get(family, PRIME_MODES)
        self.mode.blockSignals(True)
        try:
            self.mode.clear()
            self.mode.addItems(choices)
            if previous in choices:
                self.mode.setCurrentText(previous)
        finally:
            self.mode.blockSignals(False)
        descriptions = {
            "Prime research": "Prime masks and prime constellations",
            "Scientific controls": "Arithmetic controls used to test prime-specific effects",
            "Modular diagnostics": "Residue and multiplicative structure diagnostics",
        }
        self.mode_help.setText(descriptions.get(family, ""))
        self.mode_changed(self.mode.currentText())

    def set_mode(self, mode):
        family = next(
            (name for name, choices in MODE_GROUPS.items() if mode in choices),
            "Prime research",
        )
        if self.mode_family.currentText() != family:
            self.mode_family.setCurrentText(family)
        self.mode.setCurrentText(mode)

    def schedule_render(self, *args):
        self.timer.start(get_config().redraw_delay_ms)

    def apply_app_config(self, config):
        """Apply a configuration profile without restarting the application."""
        set_config(config)
        clear_volume_cache()
        self.backend_label.setText(configure_backend(self.backend.currentText()))
        if self.scan_tab is not None:
            self.scan_tab.trials.setValue(config.baseline_trials)
        self.schedule_render()

    def lock_ratio_changed(self, enabled):
        self._locked_dims = (
            self.x_spin.value(),
            self.y_spin.value(),
            self.z_spin.value(),
        )

    def dimension_changed(self, axis):
        if self.lock_ratio.isChecked() and not self._ratio_guard:
            old = dict(zip("xyz", self._locked_dims))
            source = {"x": self.x_spin, "y": self.y_spin, "z": self.z_spin}[
                axis
            ].value()
            factor = source / max(1, old[axis])
            self._ratio_guard = True
            try:
                for name, spin in (
                    ("x", self.x_spin),
                    ("y", self.y_spin),
                    ("z", self.z_spin),
                ):
                    if name != axis:
                        spin.setValue(max(1, round(old[name] * factor)))
            finally:
                self._ratio_guard = False
            self._locked_dims = (
                self.x_spin.value(),
                self.y_spin.value(),
                self.z_spin.value(),
            )
        self.plane_changed()

    def adjust_level(self, delta):
        self.level.setValue(
            max(
                self.level.minimum(),
                min(self.level.maximum(), self.level.value() + int(delta)),
            )
        )
        self.level_value.setText(f"{self.level.value() + 1}/{self.level.maximum() + 1}")

    def plane_changed(self, *args):
        cfg = self.config()
        maximum = {"XY": cfg.z, "XZ": cfg.y, "YZ": cfg.x}[self.plane.currentText()] - 1
        self.level.setMaximum(maximum)
        self.level.setValue(min(self.level.value(), maximum))
        self.level_value.setText(f"{self.level.value() + 1}/{maximum + 1}")
        self.schedule_render()

    def backend_changed(self, *args):
        self.backend_label.setText(configure_backend(self.backend.currentText()))
        clear_volume_cache()
        self.schedule_render()

    def show_gpu_diagnostics(self):
        detail = backend_error() or "CUDA backend operational."
        QMessageBox.information(
            self,
            "GPU diagnostics",
            f"{backend_summary()}\n\n{detail}\n\n"
            "For CUDA 12 run inside the active virtual environment:\n"
            "python -m pip install --upgrade -r requirements-gpu-cuda12.txt",
        )

    def overlay_options_changed(self, *args):
        is_fft = self.view_mode.currentText() == "FFT 2D"
        self.image_view.set_overlays(
            self.show_numbers.isChecked() and not is_fft,
            self.show_grid.isChecked() and not is_fft,
        )

    def set_dims(self, x, y, z):
        self._ratio_guard = True
        try:
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.z_spin.setValue(z)
        finally:
            self._ratio_guard = False
        self._locked_dims = (x, y, z)
        self.plane_changed()

    def apply_preset(self, x, y, z, mode=None, overlay=None, view=None):
        self.set_dims(x, y, z)
        z_diamond_preset = (x, y, z) == (71, 30, 30)
        if z_diamond_preset:
            self.placement.setCurrentText("Linear")
        if mode is not None:
            self.set_mode(mode)
        if overlay is not None:
            self.overlay.setChecked(overlay)
        if view is not None:
            self.view_mode.setCurrentText(view)
        if mode == "Residues modulo N":
            self.param.setValue(7)
        self.level.setValue(self.level.maximum() if z_diamond_preset else 0)
        self.schedule_render()

    def render(self):
        experiment_started_at = utc_now()
        try:
            cfg = self.config()
            total = cfg.x * cfg.y * cfg.z
            maximum = get_config().max_volume
            if total > maximum:
                raise ValueError(
                    f"Volume {total:,} exceeds the {maximum:,}-cell safety limit"
                )
            render_projection = _projection_operation_memory_estimate(
                cfg, self.plane.currentText(), public_copy=True,
            )
            plane_cells = {
                "XY": cfg.x * cfg.y,
                "XZ": cfg.x * cfg.z,
                "YZ": cfg.y * cfg.z,
            }[self.plane.currentText()]
            require_memory(compose_estimates(
                "interactive rendering",
                (
                    MemoryEstimate(
                        "retained projection",
                        persistent=render_projection.additional_peak,
                    ),
                    MemoryEstimate(
                        "analysis, RGB and QImage buffers",
                        temporary=plane_cells * 32,
                    ),
                ),
            ))
            data = projection(
                cfg,
                self.plane.currentText(),
                self.level.value(),
                self.overlay.isChecked(),
            )
            view_name = self.view_mode.currentText()
            fft_metrics = None
            if view_name == "FFT 2D":
                spectrum, fft_metrics = fft_spectrum(data, self.overlay.isChecked())
                values = spectrum.ravel()
            else:
                values = analysis_values(data, view_name, self.overlay.isChecked())
            selected = (
                np.asarray(data["hits"]).ravel() > 0
                if self.overlay.isChecked()
                else np.asarray(data["selected"]).ravel()
            )
            edges = (
                entropy_edge_mask(values) if view_name == "Entropy edges only" else None
            )
            if view_name == "FFT 2D":
                rgb = colorize_fft(values).reshape(data["proj_y"], data["proj_x"], 3)
                # QImage has a top-left origin; v160 used imshow(origin="lower").
                rgb = np.ascontiguousarray(np.flipud(rgb))
            elif cfg.mode == "Möbius μ(n)" and view_name == "Classic":
                field = np.asarray(data["mode_values"]).ravel()
                rgb = np.empty((field.size, 3), dtype=np.uint8)
                rgb[field < 0] = (215, 48, 39)
                rgb[field == 0] = (224, 224, 224)
                rgb[field > 0] = (49, 130, 189)
                rgb = rgb.reshape(data["proj_y"], data["proj_x"], 3)
            elif (
                cfg.mode in ("Divisor count τ(n)", "GCD with N")
                and view_name == "Classic"
            ):
                rgb = colorize(values, "Heatmap").reshape(
                    data["proj_y"], data["proj_x"], 3
                )
            else:
                rgb = colorize(
                    values,
                    view_name,
                    selected,
                    edges,
                    numbers=np.asarray(data["numbers"]).ravel(),
                    mode=cfg.mode,
                    param=cfg.param,
                    overlay=self.overlay.isChecked(),
                    hits=np.asarray(data["hits"]).ravel(),
                    visible_depth=data["visible_depth"],
                ).reshape(data["proj_y"], data["proj_x"], 3)
            image = QImage(
                rgb.data,
                data["proj_x"],
                data["proj_y"],
                rgb.strides[0],
                QImage.Format.Format_RGB888,
            ).copy()
            self.current_image = image
            self.current_data = data
            is_fft = view_name == "FFT 2D"
            self.image_view.set_overlays(
                self.show_numbers.isChecked() and not is_fft,
                self.show_grid.isChecked() and not is_fft,
            )
            self.image_view.set_image(
                image, np.flipud(spectrum) if is_fft else np.asarray(data["numbers"])
            )
            self.backend_label.setText(backend_summary())
            metric_text = ""
            if (
                cfg.mode == "Primes"
                and self.overlay.isChecked()
                and cfg.placement == "Linear"
            ):
                quick = current_overlay_metrics(cfg, data, self.plane.currentText())
                metric_text = (
                    f" | coprime+ {quick['coprime_alive_ratio']:.3f}"
                    f" | noncoprime+ {quick['noncoprime_alive_ratio']:.3f}"
                    f" | Hloc {quick['local_entropy_mean']:.3f}"
                    f" | edges {quick['edge_density']:.3f} | beauty {quick['beauty_score']:.3f}"
                )
            if fft_metrics is not None:
                metric_text += (
                    f" | FFT peak {fft_metrics['fft_peak_ratio']:.4f}"
                    f" | axis {fft_metrics['fft_axis_ratio']:.4f}"
                    f" | H {fft_metrics['fft_spectral_entropy']:.4f}"
                )
            self.statusBar().showMessage(
                f"{cfg.x}×{cfg.y}×{cfg.z} | {self.plane.currentText()} level {data['depth'] + 1}/{data['depth_limit']} | "
                f"selected {int(data['selected_3d'].sum()):,} | {backend_summary()}{metric_text}"
            )
            self._render_provenance = {
                "started_at": experiment_started_at,
                "completed_at": utc_now(),
                "configuration": _grid_configuration(
                    cfg,
                    self.plane.currentText(),
                    self.level.value(),
                    self.overlay.isChecked(),
                    view_name,
                ),
                "compute": _compute_record(self.backend.currentText()),
                "initial_source": self._application_source_identity,
            }
        except MemoryBudgetExceeded as exc:
            # Preserve the last successfully rendered image and its provenance.
            QMessageBox.warning(
                self,
                "Memory budget",
                f"{exc}\n\nReduce the grid dimensions or select a less "
                "memory-intensive view.",
            )
            self.statusBar().showMessage(f"Render rejected: {exc}")
        except Exception as exc:
            self.image_view.set_error(f"Rendering error:\n{exc}")
            self.statusBar().showMessage(f"Rendering error: {exc}")

    def save_png(self):
        if self.current_image is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PNG", "grid.png", "PNG (*.png)"
        )
        if path:
            output_path = Path(path)
            manifest_path = manifest_sidecar_path(output_path)
            with ExportConsistencyGuard(manifest_path, [output_path]):
                if not self.image_view.viewport().grab().save(path, "PNG"):
                    raise OSError("PNG output could not be written")
                observed = getattr(self, "_render_provenance", None)
                configuration = (
                    observed["configuration"] if observed else {"status": "not_verified"}
                )
                _write_export_manifest(
                    manifest_path,
                    "grid_screenshot",
                    [output_path.name],
                    requested_configuration=configuration,
                    effective_configuration=configuration,
                    compute=(
                        observed["compute"] if observed
                        else _compute_record(self.backend.currentText())
                    ),
                    started_at=observed["started_at"] if observed else None,
                    completed_at=observed["completed_at"] if observed else None,
                    limitations=[
                        "The PNG captures viewport zoom and overlays, which are presentation state rather than scientific array data.",
                        "The sidecar is created only after an export destination is selected.",
                    ],
                    initial_source=(observed["initial_source"] if observed else None),
                )

    def show_fft(self):
        self.view_mode.setCurrentText("FFT 2D")
        self.schedule_render()

    def show_matrix_tab(self, matrix, title):
        matrix = np.asarray(matrix, dtype=float)
        if self.analysis_tab is None:
            self.analysis_tab = QWidget()
            layout = QVBoxLayout(self.analysis_tab)
            self.analysis_title = QLabel()
            self.analysis_title.setStyleSheet(
                "font-size: 15px; font-weight: bold; padding: 4px;"
            )
            self.analysis_view = ImageView()
            self.analysis_view.set_overlays(False, False)
            layout.addWidget(self.analysis_title)
            layout.addWidget(self.analysis_view, 1)
            self.tabs.addTab(self.analysis_tab, "FFT / Heatmap")
        finite = np.nan_to_num(matrix, nan=0.0)
        rgb = colorize_fft(matrix.ravel()).reshape(finite.shape[0], finite.shape[1], 3)
        rgb = np.ascontiguousarray(np.flipud(rgb))
        image = QImage(
            rgb.data,
            finite.shape[1],
            finite.shape[0],
            rgb.strides[0],
            QImage.Format.Format_RGB888,
        ).copy()
        self.analysis_title.setText(title)
        self.analysis_view.set_image(image, np.flipud(finite))
        self.analysis_view.set_overlays(False, False)
        self.tabs.setCurrentWidget(self.analysis_tab)

    def save_fft(self):
        if self.current_data is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save FFT", "fft.png", "PNG (*.png)"
        )
        if not path:
            return
        experiment_started_at = utc_now()
        output_path = Path(path)
        manifest_path = manifest_sidecar_path(output_path)
        observed = getattr(self, "_render_provenance", None)
        fft_overlay = self.overlay.isChecked()
        import matplotlib.pyplot as plt

        with ExportConsistencyGuard(manifest_path, [output_path]):
            spectrum, metrics = fft_spectrum(self.current_data, fft_overlay)
            fig, ax = plt.subplots(figsize=(8, 7))
            try:
                image = ax.imshow(spectrum, cmap="viridis", origin="lower")
                ax.set_title(
                    f"FFT | peak={metrics['fft_peak_ratio']:.4f} axis={metrics['fft_axis_ratio']:.4f}"
                )
                fig.colorbar(image, ax=ax)
                fig.tight_layout()
                fig.savefig(path, dpi=180)
            finally:
                plt.close(fig)
            current_widgets = _grid_configuration(
                self.config(),
                self.plane.currentText(),
                self.level.value(),
                self.overlay.isChecked(),
                self.view_mode.currentText(),
            )
            source_configuration = (
                observed["configuration"] if observed is not None
                else {"status": "not_verified"}
            )
            requested_configuration = {
                "current_widgets_at_export": current_widgets,
                "fft_export_options": {"overlay": fft_overlay, "dpi": 180},
            }
            effective_configuration = {
                "current_data_source": source_configuration,
                "fft_export_options": {"overlay": fft_overlay, "dpi": 180},
                "fft_metrics": metrics,
            }
            _write_export_manifest(
                manifest_path,
                "fft_screenshot",
                [output_path.name],
                requested_configuration=requested_configuration,
                effective_configuration=effective_configuration,
                compute=_compute_record(self.backend.currentText()),
                started_at=experiment_started_at,
                completed_at=utc_now(),
                limitations=["The FFT export sidecar is created only after an export destination is selected."],
                initial_source=(
                    observed["initial_source"] if observed is not None
                    else self._application_source_identity
                ),
            )

    def show_3d(self):
        try:
            if self.current_data is None:
                return
            cfg = self.config()
            selected = self.current_data["selected_3d"]
            selected_points = (
                int(np.count_nonzero(selected))
                if self.selected_only_3d.isChecked()
                else min(selected.size, get_config().max_3d_points)
            )
            require_memory(estimate_3d(selected.shape, selected_points=selected_points))
            import pyqtgraph.opengl as gl

            if self.selected_only_3d.isChecked():
                z, y, x = np.nonzero(selected)
                selected_colors = True
            else:
                z, y, x = np.indices(selected.shape)
                z, y, x = z.ravel(), y.ravel(), x.ravel()
                selected_colors = selected.ravel()
            if not len(x):
                QMessageBox.information(
                    self, "3D view", "No selected points to display."
                )
                return
            max_points = get_config().max_3d_points
            if len(x) > max_points:
                take = np.linspace(0, len(x) - 1, max_points, dtype=np.int64)
                x, y, z = x[take], y[take], z[take]
                if isinstance(selected_colors, np.ndarray):
                    selected_colors = selected_colors[take]
            geometry = self.geometry_3d.currentText()
            spherical = geometry != "Cartesian grid"
            self._gl_is_spherical = spherical
            rotation = (
                self.shell_rotation.value()
                if geometry == "Rotating spherical shells"
                else 0.0
            )
            if spherical:
                positions = spherical_shell_positions(
                    x,
                    y,
                    z,
                    cfg.x,
                    cfg.y,
                    self.shell_inner_radius.value(),
                    self.shell_spacing.value(),
                    rotation,
                )
            else:
                positions = np.column_stack((x, y, z)).astype(
                    np.float32, copy=False
                )
            colors = np.empty((len(positions), 4), dtype=np.float32)
            if isinstance(selected_colors, np.ndarray):
                colors[:] = (0.34, 0.58, 0.82, 0.42)
                colors[selected_colors] = (1.0, 0.22, 0.03, 0.96)
            else:
                colors[:] = (1.0, 0.22, 0.03, 0.96)
            if spherical:
                shell_fraction = np.asarray(z, dtype=np.float32) / max(1, cfg.z - 1)
                star_mask = (
                    np.asarray(selected_colors, dtype=bool)
                    if isinstance(selected_colors, np.ndarray)
                    else np.ones(len(positions), dtype=bool)
                )
                # Inner stars are cool white-blue; outer shells gradually warm
                # to gold, making radial depth readable without changing size.
                colors[star_mask, 0] = 0.72 + 0.28 * shell_fraction[star_mask]
                colors[star_mask, 1] = 0.88 - 0.20 * shell_fraction[star_mask]
                colors[star_mask, 2] = 1.00 - 0.62 * shell_fraction[star_mask]
                colors[star_mask, 3] = 0.96
            if self.gl_dialog is None:
                self._create_3d_window(gl)
            # A GLViewWidget needs to be exposed at least once before its
            # OpenGL context is usable. This matters when it lives in a tab
            # that was created while hidden.
            self.tabs.setCurrentWidget(self.gl_dialog)
            self.gl_dialog.show()
            self.gl_view.show()
            QApplication.processEvents()
            context = self.gl_view.context()
            if context is None or not context.isValid():
                raise RuntimeError(
                    "Qt did not create a valid OpenGL context for the embedded 3D tab."
                )
            for item in list(self.gl_items):
                self.gl_view.removeItem(item)
            self.gl_items.clear()
            self.gl_title.setText(
                f"Prime Star Atlas — {geometry} — {cfg.mode} — "
                f"{len(positions):,} points"
            )
            scatter = gl.GLScatterPlotItem(
                pos=positions,
                color=colors,
                size=get_config().point_size_3d,
                pxMode=True,
            )
            scatter.setGLOptions("translucent")
            self.gl_view.addItem(scatter)
            axis = gl.GLAxisItem()
            outer_radius = self.shell_inner_radius.value() + max(
                0, cfg.z - 1
            ) * self.shell_spacing.value()
            self._gl_outer_radius = outer_radius
            if spherical:
                axis.setSize(
                    x=max(1.0, outer_radius),
                    y=max(1.0, outer_radius),
                    z=max(1.0, outer_radius),
                )
            else:
                axis.setSize(
                    x=max(1, cfg.x - 1),
                    y=max(1, cfg.y - 1),
                    z=max(1, cfg.z - 1),
                )
            self.gl_view.addItem(axis)
            self.gl_items.extend((scatter, axis))
            if spherical:
                angles = np.linspace(0.0, 2.0 * np.pi, 257, dtype=np.float32)
                zero = np.zeros_like(angles)
                cosine = outer_radius * np.cos(angles)
                sine = outer_radius * np.sin(angles)
                for ring_positions in (
                    np.column_stack((cosine, sine, zero)),
                    np.column_stack((cosine, zero, sine)),
                    np.column_stack((zero, cosine, sine)),
                ):
                    ring = gl.GLLinePlotItem(
                        pos=ring_positions.astype(np.float32, copy=False),
                        color=(0.35, 0.48, 0.68, 0.28),
                        width=1.0,
                        antialias=True,
                    )
                    ring.setGLOptions("translucent")
                    self.gl_view.addItem(ring)
                    self.gl_items.append(ring)
                self._gl_center = QVector3D(0, 0, 0)
                self._gl_distance = max(10.0, outer_radius * 3.0)
                self._gl_pan_step = max(0.5, outer_radius * 0.06)
            else:
                grid = gl.GLGridItem()
                grid.setSize(x=cfg.x, y=cfg.y)
                grid.translate(cfg.x / 2, cfg.y / 2, 0)
                grid.setColor((105, 120, 145, 115))
                self.gl_view.addItem(grid)
                self.gl_items.append(grid)
                self._gl_center = QVector3D(
                    (cfg.x - 1) / 2, (cfg.y - 1) / 2, (cfg.z - 1) / 2
                )
                self._gl_distance = max(10.0, max(cfg.x, cfg.y, cfg.z) * 1.8)
                self._gl_pan_step = max(1.0, max(cfg.x, cfg.y, cfg.z) * 0.06)
            self._set_3d_camera(24, 42)
            self.gl_status.setText(
                f"Loaded {len(positions):,} points | {geometry} | "
                f"r={self.shell_inner_radius.value():.2f}..{outer_radius:.2f}"
                if spherical
                else f"Loaded {len(positions):,} Cartesian points"
            )
            self.gl_view.update()
            QApplication.processEvents()
        except MemoryBudgetExceeded as exc:
            QMessageBox.warning(
                self,
                "Memory budget",
                f"{exc}\n\nReduce X, Y or Z, or enable selected-points-only.",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "GPU 3D error",
                f"{exc}\n\nInstall the OpenGL dependencies with:\n"
                "python -m pip install pyqtgraph PyOpenGL",
            )

    def _create_3d_window(self, gl):
        self.gl_dialog = QWidget()
        layout = QVBoxLayout(self.gl_dialog)
        self.gl_title = QLabel("GPU 3D")
        self.gl_title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px;")
        layout.addWidget(self.gl_title)
        toolbar = QHBoxLayout()
        controls = (
            ("Reset", lambda: self._set_3d_camera(24, 42)),
            ("Observer 0,0,0", self._set_3d_center_observer),
            ("Top", lambda: self._set_3d_camera(90, -90)),
            ("Front", lambda: self._set_3d_camera(0, -90)),
            ("Side", lambda: self._set_3d_camera(0, 0)),
            ("←", lambda: self._pan_3d(-1, 0, 0)),
            ("→", lambda: self._pan_3d(1, 0, 0)),
            ("↑", lambda: self._pan_3d(0, 1, 0)),
            ("↓", lambda: self._pan_3d(0, -1, 0)),
            ("Z+", lambda: self._pan_3d(0, 0, 1)),
            ("Z−", lambda: self._pan_3d(0, 0, -1)),
            ("Zoom +", lambda: self._zoom_3d(0.8)),
            ("Zoom −", lambda: self._zoom_3d(1.25)),
        )
        for text, callback in controls:
            button = QPushButton(text)
            button.clicked.connect(callback)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        help_label = QLabel(
            "Left drag: rotate | Middle/right drag: pan | Wheel: zoom | Buttons: precise navigation"
        )
        layout.addWidget(help_label)
        self.gl_status = QLabel("No 3D dataset loaded")
        layout.addWidget(self.gl_status)
        self.gl_view = gl.GLViewWidget()
        self.gl_view.setBackgroundColor((14, 18, 27))
        layout.addWidget(self.gl_view, 1)
        self.tabs.addTab(self.gl_dialog, "3D")

    def _set_3d_camera(self, elevation, azimuth):
        if self.gl_view is not None:
            self.gl_view.setCameraPosition(
                pos=self._gl_center,
                distance=self._gl_distance,
                elevation=elevation,
                azimuth=azimuth,
            )

    def _set_3d_center_observer(self):
        """Place the camera at the origin while targeting the outer sphere."""
        if self.gl_view is None:
            return
        if not self._gl_is_spherical:
            QMessageBox.information(
                self,
                "Center observer",
                "Observer 0,0,0 is available for spherical geometries.",
            )
            return
        distance = max(1.0, float(self._gl_outer_radius))
        target = QVector3D(distance, 0.0, 0.0)
        self.gl_view.setCameraPosition(
            pos=target,
            distance=distance,
            elevation=0,
            azimuth=90,
        )
        # GLViewWidget derives the camera from target, distance and rotation.
        # Translating the target by -cameraPosition moves the derived camera
        # exactly to the world origin without relying on PyQtGraph's internal
        # sign convention.
        camera = self.gl_view.cameraPosition()
        corrected_target = target - camera
        self.gl_view.setCameraPosition(
            pos=corrected_target,
            distance=distance,
            elevation=0,
            azimuth=90,
        )
        camera = self.gl_view.cameraPosition()
        self.gl_status.setText(
            "Observer inside shells | camera "
            f"({camera.x():.3f}, {camera.y():.3f}, {camera.z():.3f})"
        )
        self.gl_view.update()

    def _pan_3d(self, dx, dy, dz):
        if self.gl_view is not None:
            self.gl_view.pan(
                dx * self._gl_pan_step,
                dy * self._gl_pan_step,
                dz * self._gl_pan_step,
                relative="view",
            )

    def _zoom_3d(self, factor):
        if self.gl_view is not None:
            self._gl_distance = max(0.1, self._gl_distance * factor)
            self.gl_view.setCameraPosition(distance=self._gl_distance)

    def open_scan(self):
        if self.scan_tab is None:
            self.scan_tab = ModuleScanTab(self)
            self.tabs.addTab(self.scan_tab, "Module scan")
        self.tabs.setCurrentWidget(self.scan_tab)

    def open_placement_comparison(self):
        if self.comparison_tab is None:
            self.comparison_tab = PlacementComparisonTab(self)
            self.tabs.addTab(self.comparison_tab, "Placement comparison")
        self.tabs.setCurrentWidget(self.comparison_tab)

    def closeEvent(self, event):
        if self.comparison_tab is not None and not self.comparison_tab.stop():
            event.ignore()
            QMessageBox.information(
                self,
                "Comparison still stopping",
                "The placement comparison is still stopping. Wait and close again.",
            )
            return
        if (
            self.scan_tab is not None
            and self.scan_tab.thread
            and self.scan_tab.thread.isRunning()
        ):
            self.scan_tab.worker.cancel()
            self.scan_tab.thread.quit()
            if not self.scan_tab.thread.wait(5000):
                event.ignore()
                QMessageBox.information(
                    self,
                    "Scan still stopping",
                    "The current numerical step is still running. Wait for the scan to stop, then close again.",
                )
                return
        super().closeEvent(event)


def run():
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Prime Grid Atlas")
    try:
        load_default_config_if_present()
    except Exception as exc:
        QMessageBox.warning(
            None, "Configuration", f"Default configuration was not loaded:\n{exc}"
        )
    window = MainWindow()
    window.show()
    return app.exec()
