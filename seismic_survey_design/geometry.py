import geopandas as gpd
from shapely.geometry import Point


def transform_to_local(
    gdf: gpd.GeoDataFrame,
    center: gpd.GeoDataFrame,
    angle: float | int,
    origin: gpd.GeoDataFrame | None = None,
) -> gpd.GeoDataFrame:
    """Transform global geometries into a local coordinate system.

    The center point is translated to (0, 0), and the geometries
    are rotated by -angle degrees. The returned GeoDataFrame has
    no CRS assigned.

    Args:
        gdf: GeoDataFrame containing global geometries.
        center: GeoDataFrame containing exactly one global center point.
        angle: Survey rotation angle in degrees.
        origin: Optional rotation origin in local coordinates.

    Returns:
        A copy of gdf transformed into local coordinates, without a CRS.
    """

    if gdf.crs is None or center.crs is None:
        raise ValueError("CRS of gdf and center must be defined.")

    if gdf.crs != center.crs:
        raise ValueError("CRS of gdf and center must be the same.")

    if len(center) != 1 or center.geometry.iloc[0].geom_type != "Point":
        raise ValueError("center must contain exactly one Point.")

    center_point = center.geometry.iloc[0]

    if origin is not None:
        if len(origin) != 1 or origin.geometry.iloc[0].geom_type != "Point":
            raise ValueError("origin must contain exactly one Point.")
        rotation_origin = origin.geometry.iloc[0]
    else:
        rotation_origin = Point(0, 0)

    geom = gdf.geometry.translate(
        xoff=-center_point.x,
        yoff=-center_point.y,
    ).rotate(
        angle=-angle,
        origin=rotation_origin,
        use_radians=False,
    )

    result = gdf.copy()
    result.geometry = geom
    result = result.set_crs(None, allow_override=True)

    return result
