"""Prime Grid Atlas v1.1.0 — PySide6 entry point.

The application now keeps scan, FFT and OpenGL inside the main tab widget, so
Qt can use the native Wayland/EGL backend.  Forcing XWayland here caused blank
OpenGL output on hybrid AMD/NVIDIA systems.
"""

from qt_app import run


if __name__ == "__main__":
    raise SystemExit(run())
