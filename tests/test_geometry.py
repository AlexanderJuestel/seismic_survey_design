import geopandas as gpd
import pytest
from shapely.geometry import Point, Polygon

from seismic_survey_design.geometry import transform_to_local


@pytest.fixture
def valid_gdf():
    return gpd.GeoDataFrame(
        geometry=[Polygon([(10, 10), (14, 10), (14, 12), (10, 12)])],
        crs="EPSG:25832",
    )


@pytest.fixture
def valid_center():
    return gpd.GeoDataFrame(
        geometry=[Point(12, 11)],
        crs="EPSG:25832",
    )


def test_transform_to_local_rejects_missing_gdf_crs(
    valid_center,
):
    gdf = gpd.GeoDataFrame(
        geometry=[Point(10, 10)],
    )

    with pytest.raises(ValueError, match="CRS"):
        transform_to_local(gdf, valid_center, angle=0)


def test_transform_to_local_rejects_missing_center_crs(
    valid_gdf,
):
    center = gpd.GeoDataFrame(
        geometry=[Point(12, 11)],
    )

    with pytest.raises(ValueError, match="CRS"):
        transform_to_local(valid_gdf, center, angle=0)


def test_transform_to_local_rejects_different_crs(
    valid_gdf,
):
    center = gpd.GeoDataFrame(
        geometry=[Point(12, 11)],
        crs="EPSG:4326",
    )

    with pytest.raises(ValueError, match="same"):
        transform_to_local(valid_gdf, center, angle=0)


@pytest.mark.parametrize(
    "center",
    [
        gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:25832",
        ),
        gpd.GeoDataFrame(
            geometry=[Point(12, 11), Point(13, 12)],
            crs="EPSG:25832",
        ),
        gpd.GeoDataFrame(
            geometry=[Polygon([(10, 10), (14, 10), (14, 12), (10, 12)])],
            crs="EPSG:25832",
        ),
    ],
    ids=["empty", "multiple-points", "wrong-geometry-type"],
)
def test_transform_to_local_rejects_invalid_center(
    valid_gdf,
    center,
):
    with pytest.raises(ValueError, match="center"):
        transform_to_local(valid_gdf, center, angle=0)


@pytest.mark.parametrize(
    "origin",
    [
        gpd.GeoDataFrame(
            geometry=[],
        ),
        gpd.GeoDataFrame(
            geometry=[Point(0, 0), Point(1, 1)],
        ),
        gpd.GeoDataFrame(
            geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
        ),
    ],
    ids=["empty", "multiple-points", "wrong-geometry-type"],
)
def test_transform_to_local_rejects_invalid_origin(
    valid_gdf,
    valid_center,
    origin,
):
    with pytest.raises(ValueError, match="origin"):
        transform_to_local(
            valid_gdf,
            valid_center,
            angle=0,
            origin=origin,
        )


def test_transform_to_local_accepts_explicit_origin(
    valid_gdf,
    valid_center,
):
    origin = gpd.GeoDataFrame(
        geometry=[Point(0, 0)],
    )

    result = transform_to_local(
        valid_gdf,
        valid_center,
        angle=0,
        origin=origin,
    )

    assert result.crs is None
    assert len(result) == 1


def test_transform_to_local_uses_explicit_origin(valid_gdf, valid_center):
    origin = gpd.GeoDataFrame(
        geometry=[Point(1, 0)],
    )

    result = transform_to_local(
        gdf=valid_gdf,
        center=valid_center,
        angle=90,
        origin=origin,
    )

    assert result.crs is None
    assert len(result) == 1
    assert result.geometry.iloc[0].is_valid


def test_transform_to_local_uses_default_rotation_origin(valid_gdf, valid_center):
    result = transform_to_local(
        gdf=valid_gdf,
        center=valid_center,
        angle=90,
        origin=None,
    )

    assert result.crs is None
    assert len(result) == 1
    assert result.geometry.iloc[0].is_valid
