from pathlib import Path
from typing import Literal

import geopandas as gpd
import pyproj


def _validate_string(
    arg: str | None,
    name: str,
) -> str | None:
    """Validate that an argument is a string or None."""
    if arg is None:
        return None

    if not isinstance(arg, str):
        raise TypeError(f"'{name}' must be a string or None, got {type(arg).__name__}.")

    return arg


def _validate_float_int(
    arg: float | int | None,
    name: str,
    greater_than: float | int | None = None,
    smaller_than: float | int | None = None,
) -> float | int | None:
    """
    Validate a numeric argument and optional strict bounds.

    Args:
        arg: Numeric value to validate, or None.
        name: Parameter name used in error messages.
        greater_than: Optional exclusive lower bound.
        smaller_than: Optional exclusive upper bound.

    Returns:
        The original numeric value, or None.

    Raises:
        TypeError: If the value is not an int, float, or None,
            or if it is a boolean.
        ValueError: If the value violates either bound.
    """
    if arg is None:
        return None

    # bool is a subclass of int, so it must be rejected explicitly.
    if isinstance(arg, bool) or not isinstance(arg, (int, float)):
        raise TypeError(
            f"'{name}' must be a float, int or None, got {type(arg).__name__}."
        )

    if greater_than is not None and arg <= greater_than:
        raise ValueError(f"'{name}' must be greater than {greater_than}")

    if smaller_than is not None and arg >= smaller_than:
        raise ValueError(f"'{name}' must be smaller than {smaller_than}")

    return arg


def _validate_gdf(
    arg: str | gpd.GeoDataFrame,
    reference_system: Literal["local", "global"],
    geom_type: Literal["Point", "LineString", "Polygon"] | None = None,
    crs: str | pyproj.CRS | None = None,
) -> gpd.GeoDataFrame:
    """Load and validate a GeoDataFrame.

    Parameters
    ----------
    arg : str or geopandas.GeoDataFrame
        Path to a vector file or an existing GeoDataFrame.
    reference_system : {"local", "global"}
        Reference system of the input geometry. Global geometries are
        transformed to ``crs`` if necessary.
    geom_type : {"Point", "LineString", "Polygon"}, optional
        Expected geometry type.
    crs : str or pyproj.CRS, optional
        Target CRS for global geometries.

    Returns
    -------
    geopandas.GeoDataFrame
        Validated GeoDataFrame.

    Raises
    ------
    TypeError
        If ``arg`` has an unsupported type.
    ValueError
        If the reference system, CRS, number of geometries or geometry
        type is invalid.
    FileNotFoundError
        If the specified file does not exist.
    """
    # Validate reference system
    if reference_system not in ("local", "global"):
        raise ValueError("reference_system must be either 'local' or 'global'.")

    # Load vector data if a path is provided
    if isinstance(arg, str):
        path = Path(arg)

        if not path.is_file():
            raise FileNotFoundError(f"Vector file not found: {path}")

        gdf = gpd.read_file(path)

    elif isinstance(arg, gpd.GeoDataFrame):
        gdf = arg.copy()

    else:
        raise TypeError("arg must be a file path (str) or a gpd.GeoDataFrame.")

    # Check for empty GeoDataFrames
    if gdf.empty:
        raise ValueError("The GeoDataFrame is empty.")

    # Transform global geometries to the target CRS
    if reference_system == "global":
        if gdf.crs is None:
            raise ValueError(
                "The input GeoDataFrame has no CRS. "
                "A CRS is required for global geometries."
            )

        if crs is None:
            raise ValueError("crs must be provided for global geometries.")

        target_crs = pyproj.CRS.from_user_input(crs)

        if not gdf.crs.equals(target_crs):
            gdf = gdf.to_crs(target_crs)

    # Check number of geometries
    if len(gdf) != 1:
        raise ValueError(f"Expected exactly one geometry, but found {len(gdf)}.")

    # Check geometry type
    if geom_type is not None and gdf.geom_type.iloc[0] != geom_type:
        raise ValueError(
            f"Expected geometry type '{geom_type}', "
            f"but found '{gdf.geom_type.iloc[0]}'."
        )

    return gdf
