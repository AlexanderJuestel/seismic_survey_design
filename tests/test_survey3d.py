import geopandas as gpd
import pyproj
import pytest
from shapely.geometry import Point, Polygon

from seismic_survey_design.survey3d import Survey3D


class TestSurvey3D:
    """Tests for the Survey3D class."""

    def test_default_initialization(self):
        """Optional parameters should accept None."""
        survey = Survey3D()

        assert survey.design_name is None
        assert survey.project_name is None
        assert survey.project_location is None
        assert survey.license_name is None
        assert survey.target_name_shallow is None
        assert survey.target_name_deep is None

        assert isinstance(survey.target_area_center_point_gdf_local, gpd.GeoDataFrame)
        assert (
            survey.target_area_center_point_gdf_local.iloc[0].geometry.wkt
            == "POINT (0 0)"
        )

        assert survey.survey_rotation == 0.0
        assert survey.target_area_gdf_global is None

        assert survey.z_min is None
        assert survey.z_max is None
        assert survey.x_min is None
        assert survey.x_max is None
        assert survey.x_max_to_z_max_ratio is None

        assert survey.theta_inline is None
        assert survey.theta_crossline is None
        assert survey.target_size is None

        assert survey.crs == pyproj.CRS.from_epsg(25832)

    def test_parameter_initialization(self):
        """Valid parameters should be stored correctly."""
        survey = Survey3D(
            design_name="Survey Design 1",
            project_name="Reallabor Geothermie Rheinland",
            project_location="Aachen-Weisweiler",
            license_name="Aachen-Weisweiler",
            target_name_shallow="Base Tertiary",
            target_name_deep="Kohlenkalk/Massenkalk",
            target_area_center_point_gdf_local=gpd.GeoDataFrame(
                geometry=[Point(100, 100)]
            ),
            survey_rotation=50,
            target_area_gdf_global=gpd.GeoDataFrame(
                geometry=[
                    Polygon(
                        [
                            (299387.40051425825, 5631473.076100714),
                            (300063.16562393797, 5631786.82418735),
                            (300907.8720110376, 5630435.293967991),
                            (301849.1162709486, 5631026.588438961),
                            (303188.5792562065, 5632160.908444493),
                            (303550.59627924924, 5632474.65653113),
                            (305252.0762875499, 5630242.218222367),
                            (304902.1264986087, 5629759.52885831),
                            (304359.1009640447, 5629168.234387342),
                            (303466.12564053934, 5628371.796936648),
                            (301861.18350504996, 5627249.544165214),
                            (300340.7120082706, 5627116.804590098),
                            (300039.031155735, 5629156.167153238),
                            (299387.40051425825, 5631473.076100714),
                        ]
                    )
                ],
                crs="EPSG:25832",
            ),
            z_min=50,
            z_max=4000,
            theta_inline=30,
            theta_crossline=30,
            target_size=50,
            crs="EPSG:25832",
        )

        assert survey.design_name == "Survey Design 1"
        assert survey.project_name == "Reallabor Geothermie Rheinland"
        assert survey.project_location == "Aachen-Weisweiler"
        assert survey.license_name == "Aachen-Weisweiler"
        assert survey.target_name_shallow == "Base Tertiary"
        assert survey.target_name_deep == "Kohlenkalk/Massenkalk"
        assert isinstance(survey.target_area_center_point_gdf_local, gpd.GeoDataFrame)
        assert (
            survey.target_area_center_point_gdf_local.iloc[0].geometry.wkt
            == "POINT (100 100)"
        )

        assert isinstance(survey.target_area_gdf_global, gpd.GeoDataFrame)
        assert survey.target_area_gdf_global.crs == survey.crs

        assert survey.survey_rotation == 50
        assert survey.z_min == 50
        assert survey.z_max == 4000
        assert survey.x_min == 50
        assert survey.x_max == 4000
        assert survey.x_max_to_z_max_ratio == 1

        assert survey.theta_inline == 30
        assert survey.theta_crossline == 30
        assert survey.target_size == 50

        assert survey.crs == pyproj.CRS.from_epsg(25832)

    def test_explicit_x_max_initialization(self):
        """An explicitly provided x_max should override its default."""
        survey = Survey3D(
            z_min=50,
            z_max=4000,
            x_max=3000,
        )

        assert survey.z_min == 50
        assert survey.z_max == 4000
        assert survey.x_min == 50
        assert survey.x_max == 3000
        assert survey.x_max_to_z_max_ratio == pytest.approx(0.75)
        assert survey.crs == pyproj.CRS.from_epsg(25832)

    # ------------------------------------------------------------------
    # String parameters
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "parameter",
        [
            "design_name",
            "project_name",
            "project_location",
            "license_name",
            "target_name_shallow",
            "target_name_deep",
        ],
    )
    @pytest.mark.parametrize("value", [0, 0.0, True, False])
    def test_rejects_invalid_string_parameter_types(self, parameter, value):
        """String parameters should reject non-string values."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    # ------------------------------------------------------------------
    # z_min and z_max
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("parameter", ["z_min", "z_max"])
    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_depth_types(self, parameter, value):
        """Depth parameters should reject unsupported types."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize("parameter", ["z_min", "z_max"])
    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_depths(self, parameter, value):
        """Provided target depths must be greater than zero."""
        with pytest.raises(ValueError, match=parameter):
            Survey3D(**{parameter: value})

    def test_rejects_z_max_not_greater_than_z_min(self):
        """z_max must be greater than z_min when both are provided."""
        with pytest.raises(ValueError, match="z_max"):
            Survey3D(z_min=1000, z_max=500)

    def test_accepts_equal_z_min_and_z_max_only_when_unrelated(self):
        """A valid z_min can be set without specifying z_max."""
        survey = Survey3D(z_min=1000)

        assert survey.z_min == 1000
        assert survey.z_max is None

    # ------------------------------------------------------------------
    # x_max
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_x_max_types(self, value):
        """x_max should reject unsupported types."""
        with pytest.raises(TypeError, match="x_max"):
            Survey3D(x_max=value)

    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_x_max(self, value):
        """A provided x_max must be greater than zero."""
        with pytest.raises(ValueError, match="x_max"):
            Survey3D(x_max=value)

    def test_rejects_x_max_smaller_than_x_min(self):
        """x_max must not be smaller than x_min."""
        with pytest.raises(ValueError, match="x_max"):
            Survey3D(z_min=1000, x_max=500)

    def test_accepts_x_max_equal_to_x_min(self):
        """x_max may equal x_min."""
        survey = Survey3D(
            z_min=1000,
            z_max=2000,
            x_max=1000,
        )

        assert survey.x_max == survey.x_min == 1000

    def test_accepts_x_max_greater_than_x_min(self):
        """x_max may be greater than x_min."""
        survey = Survey3D(
            z_min=1000,
            z_max=2000,
            x_max=1500,
        )

        assert survey.x_max == 1500
        assert survey.x_min == 1000

    @pytest.mark.parametrize(
        ("z_max", "x_max", "expected_ratio"),
        [
            (4000, None, 1.0),
            (4000, 3000, 0.75),
            (2000, 1500, 0.75),
        ],
    )
    def test_calculates_x_max_to_z_max_ratio(self, z_max, x_max, expected_ratio):
        """The ratio should be calculated correctly."""
        survey = Survey3D(
            z_min=100,
            z_max=z_max,
            x_max=x_max,
        )

        assert survey.x_max_to_z_max_ratio == pytest.approx(expected_ratio)

    # ------------------------------------------------------------------
    # Target dipping angles
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_dipping_angle_types(self, parameter, value):
        """Dipping angles should reject unsupported types."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize(
        "value",
        [-5, 0, 0.0, 90, 90.0, 100],
    )
    def test_rejects_dipping_angle_outside_valid_range(self, parameter, value):
        """Dipping angles must be strictly between 0 and 90 degrees."""
        with pytest.raises(ValueError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize("value", [0.1, 30, 89.9])
    def test_accepts_valid_dipping_angles(self, parameter, value):
        """Dipping angles inside the valid range should be accepted."""
        survey = Survey3D(**{parameter: value})

        assert getattr(survey, parameter) == value

    # ------------------------------------------------------------------
    # Target size
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_target_size_types(self, value):
        """target_size should reject unsupported types."""
        with pytest.raises(TypeError, match="target_size"):
            Survey3D(target_size=value)

    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_target_size(self, value):
        """A provided target_size must be greater than zero."""
        with pytest.raises(ValueError, match="target_size"):
            Survey3D(target_size=value)

    @pytest.mark.parametrize("value", [0.1, 50, 1000])
    def test_accepts_positive_target_size(self, value):
        """Positive target sizes should be accepted."""
        survey = Survey3D(target_size=value)

        assert survey.target_size == value

    # ------------------------------------------------------------------
    # Coordinate reference system
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", [0, 0.0, True, False, None])
    def test_rejects_invalid_crs_types(self, value):
        """CRS must be a string or a pyproj.CRS object."""
        with pytest.raises(TypeError, match="CRS"):
            Survey3D(crs=value)

    def test_accepts_pyproj_crs(self):
        """A pyproj.CRS object should be accepted."""
        crs = pyproj.CRS.from_epsg(25832)

        survey = Survey3D(crs=crs)

        assert survey.crs == crs
        assert isinstance(survey.crs, pyproj.CRS)

    def test_accepts_crs_string(self):
        """A valid CRS string should be converted to pyproj.CRS."""
        survey = Survey3D(crs="EPSG:25832")

        assert survey.crs == pyproj.CRS.from_epsg(25832)
        assert isinstance(survey.crs, pyproj.CRS)

    def test_rejects_invalid_crs_string(self):
        """An invalid CRS string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid CRS"):
            Survey3D(crs="kein-koordinatensystem")

    # ------------------------------------------------------------------
    # Target Area
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", [True, 0, 0.1])
    def test_rejects_invalid_target_area_center_point_gdf_local_types(self, value):
        """target_area_center_point_gdf_local should reject unsupported types."""
        with pytest.raises(TypeError):
            Survey3D(target_area_center_point_gdf_local=value)

    @pytest.mark.parametrize("value", ["invalid_file_path"])
    def test_rejects_invalid_target_area_center_point_gdf_local_filepath(self, value):
        """target_area_center_point_gdf_local should reject unavailable files."""
        with pytest.raises(FileNotFoundError):
            Survey3D(target_area_center_point_gdf_local=value)

    def test_rejects_empty_target_area_center_point_gdf_local(self):
        """An empty target area GeoDataFrame should be rejected."""
        with pytest.raises(ValueError, match="empty"):
            Survey3D(target_area_center_point_gdf_local=gpd.GeoDataFrame(geometry=[]))

    def test_rejects_multiple_target_area_center_points_local(self):
        """Multiple geometries should be rejected."""
        gdf = gpd.GeoDataFrame(geometry=[Point(100, 100), Point(200, 200)])

        with pytest.raises(ValueError, match="exactly one geometry"):
            Survey3D(target_area_center_point_gdf_local=gdf)

    def test_rejects_wrong_target_area_center_geometry_type(self):
        """A polygon should be rejected when a point is expected."""
        gdf = gpd.GeoDataFrame(
            geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)])]
        )

        with pytest.raises(ValueError, match="Expected geometry type 'Point'"):
            Survey3D(target_area_center_point_gdf_local=gdf)

    def test_accepts_local_target_area_center_point_without_crs(self):
        """Local coordinates should not require a CRS."""
        gdf = gpd.GeoDataFrame(geometry=[Point(100, 100)])

        survey = Survey3D(target_area_center_point_gdf_local=gdf)

        assert survey.target_area_center_point_gdf_local.geometry.iloc[0] == Point(
            100, 100
        )
        assert survey.target_area_center_point_gdf_local.crs is None

    # ------------------------------------------------------------------
    # Survey rotation
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", [True, "survey_rotation"])
    def test_rejects_invalid_survey_rotation_types(self, value):
        """survey_rotation should reject unsupported types."""
        with pytest.raises(TypeError, match="survey_rotation"):
            Survey3D(survey_rotation=value)

    @pytest.mark.parametrize("value", [-5, -1, 360, 360.1, 400])
    def test_rejects_rotation_angle_outside_valid_range(self, value):
        """Survey rotation must be in the interval [0, 360)."""
        with pytest.raises(ValueError, match="survey_rotation"):
            Survey3D(survey_rotation=value)

    @pytest.mark.parametrize("value", [0, 0.0, 50, 180, 359.9])
    def test_accepts_valid_survey_rotation(self, value):
        """Survey rotation within [0, 360) should be accepted."""
        survey = Survey3D(survey_rotation=value)

        assert survey.survey_rotation == value

    # ------------------------------------------------------------------
    # Target Area gdf Global
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", [True, 0, 0.0])
    def test_rejects_invalid_target_area_gdf_global_types(self, value):
        """target_area_gdf_global should reject unsupported types."""
        with pytest.raises(TypeError):
            Survey3D(target_area_gdf_global=value)

    @pytest.mark.parametrize("value", ["invalid_file_path"])
    def test_rejects_invalid_target_area_gdf_global_filepath(self, value):
        """target_area_gdf_global should reject unavailable files."""
        with pytest.raises(FileNotFoundError):
            Survey3D(target_area_gdf_global=value)

    def test_rejects_empty_target_area_gdf_global(self):
        """An empty target area GeoDataFrame should be rejected."""
        with pytest.raises(ValueError, match="empty"):
            Survey3D(target_area_gdf_global=gpd.GeoDataFrame(geometry=[]))

    def test_rejects_multiple_target_area_gdf_global(self):
        """Multiple geometries should be rejected."""
        polygon = Polygon([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)])
        gdf = gpd.GeoDataFrame(
            geometry=[polygon, polygon],
            crs="EPSG:25832",
        )

        with pytest.raises(ValueError, match="exactly one geometry"):
            Survey3D(target_area_gdf_global=gdf)

    def test_rejects_wrong_target_area_gdf_global_geometry_type(self):
        """A point should be rejected when a polygon is expected."""
        gdf = gpd.GeoDataFrame(
            geometry=[Point(100, 100)],
            crs="EPSG:25832",
        )

        with pytest.raises(ValueError, match="Expected geometry type 'Polygon'"):
            Survey3D(target_area_gdf_global=gdf)

    def test_rejects_target_area_gdf_global_without_crs(self):
        """Global target area geometries must define a CRS."""
        gdf = gpd.GeoDataFrame(
            geometry=[Polygon([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)])]
        )

        with pytest.raises(ValueError, match="CRS"):
            Survey3D(target_area_gdf_global=gdf)

    @pytest.fixture
    def target_area_gdf_global():
        """Return a polygon in the global CRS."""
        return gpd.GeoDataFrame(
            {"id": [1]},
            geometry=[
                Polygon([
                    (10, 10),
                    (14, 10),
                    (14, 12),
                    (10, 12),
                ])
            ],
            crs="EPSG:25832",
        )
    
    def test_target_area_gdf_local_is_initialized(
        target_area_gdf_global,
    ):
        survey = Survey3D(
            target_area_gdf_global=target_area_gdf_global,
            survey_rotation=0,
        )

        assert survey.target_area_gdf_local is not None
        assert survey.target_area_gdf_local.crs is None
        assert len(survey.target_area_gdf_local) == 1
        assert (
            survey.target_area_gdf_local.geometry.iloc[0].geom_type
            == "Polygon"
        )
    
    def test_target_area_gdf_local_is_centered(
        target_area_gdf_global,
    ):
        survey = Survey3D(
            target_area_gdf_global=target_area_gdf_global,
            survey_rotation=0,
        )

        centroid = survey.target_area_gdf_local.geometry.iloc[0].centroid

        assert centroid.x == pytest.approx(0)
        assert centroid.y == pytest.approx(0)

    def test_target_area_gdf_local_respects_survey_rotation(
        target_area_gdf_global,
    ):
        survey = Survey3D(
            target_area_gdf_global=target_area_gdf_global,
            survey_rotation=90,
        )

        minx, miny, maxx, maxy = (
            survey.target_area_gdf_local.total_bounds
        )

        assert maxx - minx == pytest.approx(2)
        assert maxy - miny == pytest.approx(4)

    def test_target_area_gdf_global_remains_unchanged(
        target_area_gdf_global,
    ):
        original = target_area_gdf_global.copy()

        Survey3D(
            target_area_gdf_global=target_area_gdf_global,
            survey_rotation=45,
        )

        assert target_area_gdf_global.crs == original.crs
        assert target_area_gdf_global.geometry.equals(original.geometry)

    def test_target_area_gdf_local_is_none_without_global_target():
        survey = Survey3D(target_area_gdf_global=None)

        assert survey.target_area_gdf_global is None
        assert survey.target_area_center_point_gdf_global is None
        assert survey.target_area_gdf_local is None