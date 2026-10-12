import geopandas as gpd
import pyproj
from shapely.geometry import Point

from seismic_survey_design.geometry import transform_to_local
from seismic_survey_design.io import (
    _validate_float_int,
    _validate_gdf,
    _validate_string,
)


class Survey3D:
    """
    Define a 3D seismic survey design and its target parameters.

    The class stores project metadata, the coordinate reference system
    (CRS), target parameters, and geometric properties of the target.

    Numeric parameters are validated during initialization. Target
    depths and offsets must be positive when provided. The maximum
    target depth must exceed the minimum target depth.

    Parameters
    ----------
    design_name : str or None, optional
        Name assigned to the survey design.
    project_name : str or None, optional
        Name of the associated project.
    project_location : str or None, optional
        Geographic or administrative location of the project.
    license_name : str or None, optional
        Name of the relevant license or licensed area.
    target_name_shallow : str or None, optional
        Name of the shallow target horizon.
    target_name_deep : str or None, optional
        Name of the deep target horizon.
    z_min : float or int or None, optional
        Minimum target depth. Must be greater than zero if provided.
    z_max : float or int or None, optional
        Maximum target depth. Must be greater than zero and greater
        than ``z_min`` if both are provided.
    x_max : float or int or None, optional
        Maximum target offset. Defaults to ``z_max`` if omitted.
        Must be greater than or equal to ``x_min`` when both exist.
    target_size : float or int or None, optional
        Characteristic target size in the units used by the survey.
        Must be greater than zero if provided.
    theta_inline : float or int or None, optional
        Target dip angle in the inline direction, in degrees.
        Must be strictly between 0 and 90 degrees if provided.
    theta_crossline : float or int or None, optional
        Target dip angle in the crossline direction, in degrees.
        Must be strictly between 0 and 90 degrees if provided.
    crs : str or pyproj.CRS, optional
        Coordinate reference system identifier or CRS object.
        Defaults to ``"EPSG:25832"``.

    Attributes
    ----------
    design_name : str or None
        Name assigned to the survey design.
    project_name : str or None
        Name of the associated project.
    project_location : str or None
        Geographic or administrative location of the project.
    license_name : str or None
        Name of the relevant license or licensed area.
    target_name_shallow : str or None
        Name of the shallow target horizon.
    target_name_deep : str or None
        Name of the deep target horizon.
    z_min : float or None
        Minimum target depth.
    z_max : float or None
        Maximum target depth.
    x_min : float or None
        Minimum target offset.
    x_max : float or None
        Maximum target offset.
    x_max_to_z_max_ratio : float or None
        Ratio of ``x_max`` to ``z_max`` when both are defined.
    target_size : float or None
        Characteristic target size in the units used by the survey.
    theta_inline : float or None
        Target dip angle in the inline direction, in degrees.
    theta_crossline : float or None
        Target dip angle in the crossline direction, in degrees.
    crs : pyproj.CRS
        Coordinate reference system used for the survey.
    """

    def __init__(
        self,
        design_name: str | None = None,
        project_name: str | None = None,
        project_location: str | None = None,
        license_name: str | None = None,
        target_name_shallow: str | None = None,
        target_name_deep: str | None = None,
        z_min: float | None = None,
        z_max: float | None = None,
        x_max: float | None = None,
        target_size: float | None = None,
        theta_inline: float | None = None,
        theta_crossline: float | None = None,
        target_area_center_point_gdf_local: str | gpd.GeoDataFrame | None = None,
        target_area_gdf_global: str | gpd.GeoDataFrame | None = None,
        survey_rotation: float | int = 0.0,
        crs: str | pyproj.CRS = "EPSG:25832",
    ) -> None:
        #################################################
        # General
        #################################################
        self.design_name = _validate_string(arg=design_name, name="design_name")

        self.project_name = _validate_string(arg=project_name, name="project_name")

        self.project_location = _validate_string(
            arg=project_location, name="project_location"
        )

        self.license_name = _validate_string(arg=license_name, name="license_name")

        if not isinstance(crs, (str, pyproj.CRS)):
            raise TypeError("The CRS must be provided as a string or pyproj CRS object")

        try:
            self.crs = pyproj.CRS.from_user_input(crs)
        except (pyproj.exceptions.CRSError, ValueError) as exc:
            raise ValueError(f"Invalid CRS: {crs!r}") from exc

        #################################################
        # Target
        #################################################
        # Target Names
        self.target_name_shallow = _validate_string(
            arg=target_name_shallow, name="target_name_shallow"
        )

        self.target_name_deep = _validate_string(
            arg=target_name_deep, name="target_name_deep"
        )

        # Target Depths
        self.z_min = _validate_float_int(arg=z_min, name="z_min", greater_than=0)

        self.z_max = _validate_float_int(arg=z_max, name="z_max", greater_than=0)

        if (
            self.z_min is not None
            and self.z_max is not None
            and self.z_max <= self.z_min
        ):
            raise ValueError("'z_max' must be greater than 'z_min'")

        # Target Offsets
        validated_x_max = _validate_float_int(
            arg=x_max,
            name="x_max",
            greater_than=0,
        )

        self.x_min = self.z_min
        self.x_max = self.z_max if validated_x_max is None else validated_x_max

        if (
            self.x_max is not None
            and self.x_min is not None
            and self.x_max < self.x_min
        ):
            raise ValueError("'x_max' must be greater than or equal to 'x_min'")

        # Target Offset Ratio
        self.x_max_to_z_max_ratio = (
            self.x_max / self.z_max
            if self.x_max is not None and self.z_max is not None
            else None
        )

        # Target Dipping Angle Inline
        self.theta_inline = _validate_float_int(
            arg=theta_inline, name="theta_inline", greater_than=0, smaller_than=90
        )

        # Target Dipping Angle Crossline
        self.theta_crossline = _validate_float_int(
            arg=theta_crossline, name="theta_crossline", greater_than=0, smaller_than=90
        )

        # Target Size
        self.target_size = _validate_float_int(
            arg=target_size, name="target_size", greater_than=0
        )

        #################################################
        # Target Area
        #################################################
        # Target Area Center Point Local
        if target_area_center_point_gdf_local is None:
            target_area_center_point_gdf_local = gpd.GeoDataFrame(
                geometry=[Point(0, 0)]
            )

        self.target_area_center_point_gdf_local = _validate_gdf(
            arg=target_area_center_point_gdf_local,
            reference_system="local",
            geom_type="Point",
            crs=None,
        )

        # Survey Rotation
        self.survey_rotation = _validate_float_int(
            arg=survey_rotation,
            name="survey_rotation",
            greater_than=-1,
            smaller_than=360,
        )

        if target_area_gdf_global is not None:
            self.target_area_gdf_global = _validate_gdf(
                arg=target_area_gdf_global,
                reference_system="global",
                geom_type="Polygon",
                crs=self.crs,
            )

            self.target_area_center_point_gdf_global = _validate_gdf(
                arg=gpd.GeoDataFrame(
                    geometry=[self.target_area_gdf_global.geometry.iloc[0].centroid],
                    crs=self.crs,
                ),
                reference_system="global",
                geom_type="Point",
                crs=self.crs,
            )

            self.target_area_gdf_local = transform_to_local(
                gdf=self.target_area_gdf_global,
                center=self.target_area_center_point_gdf_global,
                angle=self.survey_rotation,
                origin=gpd.GeoDataFrame(geometry=[Point(0, 0)]),
            )
        else:
            self.target_area_gdf_global = target_area_gdf_global
            self.target_area_center_point_gdf_global = None
            self.target_area_gdf_local = None
