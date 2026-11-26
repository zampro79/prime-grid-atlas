import numpy as np

VALID_PLANES = ("XY", "XZ", "YZ")


def _validate_plane(plane):
    if plane not in VALID_PLANES:
        raise ValueError(f"Unsupported plane: {plane!r}; expected one of {VALID_PLANES}")


def spherical_shell_positions(
    x_indices,
    y_indices,
    z_indices,
    dim_x,
    dim_y,
    inner_radius=5.0,
    shell_spacing=1.0,
    rotation_degrees=0.0,
):
    """Map grid indices to equal-area concentric spherical shells."""
    x = np.asarray(x_indices, dtype=np.float64)
    y = np.asarray(y_indices, dtype=np.float64)
    z = np.asarray(z_indices, dtype=np.float64)
    theta = 2.0 * np.pi * ((x + 0.5) / max(1, int(dim_x)))
    theta += np.deg2rad(float(rotation_degrees)) * z
    height = 1.0 - 2.0 * ((y + 0.5) / max(1, int(dim_y)))
    height = np.clip(height, -1.0, 1.0)
    horizontal = np.sqrt(np.maximum(0.0, 1.0 - height * height))
    radius = max(0.1, float(inner_radius)) + z * max(0.01, float(shell_spacing))
    return np.column_stack(
        (
            radius * horizontal * np.cos(theta),
            radius * horizontal * np.sin(theta),
            radius * height,
        )
    ).astype(np.float32, copy=False)


def plane_dimensions(plane, dim_x, dim_y, dim_z):
    _validate_plane(plane)
    if plane == "XY":
        return dim_x, dim_y
    if plane == "XZ":
        return dim_x, dim_z
    return dim_y, dim_z


def get_depth_limit_for_plane(plane, dim_x, dim_y, dim_z):
    _validate_plane(plane)
    if plane == "XY":
        return dim_z
    if plane == "XZ":
        return dim_y
    return dim_x


def get_plane_data(plane, depth_index, overlay_enabled, numbers_3d, selected_3d):
    _validate_plane(plane)
    depth_index = max(0, depth_index)

    if plane == "XY":
        plane_numbers = numbers_3d[depth_index, :, :]
        plane_selected = selected_3d[depth_index, :, :]
        plane_hits = selected_3d[: depth_index + 1, :, :].sum(axis=0, dtype=np.int32)
    elif plane == "XZ":
        plane_numbers = numbers_3d[:, depth_index, :]
        plane_selected = selected_3d[:, depth_index, :]
        plane_hits = selected_3d[:, : depth_index + 1, :].sum(axis=1, dtype=np.int32)
    else:  # YZ
        # Array layout is (Z, Y): rows are Z and columns are Y, matching
        # plane_dimensions() which declares proj_x=Y and proj_y=Z.
        plane_numbers = numbers_3d[:, :, depth_index]
        plane_selected = selected_3d[:, :, depth_index]
        plane_hits = selected_3d[:, :, : depth_index + 1].sum(axis=2, dtype=np.int32)

    return {
        "numbers": np.asarray(plane_numbers),
        "selected": np.asarray(plane_selected),
        "hits": np.asarray(plane_hits),
        "visible_depth": depth_index + 1 if overlay_enabled else 1,
    }
