from seismic_survey_design.io import _validate_string

import pyproj

class Survey3D:
    def __init__(self,
                 design_name: str | None = None,
                 project_name: str | None = None, 
                 project_location: str | None = None,
                 license_name: str | None = None,
                 crs: str | pyproj.crs.crs.CRS = 'EPSG:25832'):
        #################################################
        # General
        #################################################
        self.design_name = _validate_string(arg=design_name,
                                            name='design_name')     
            
        self.project_name = _validate_string(arg=project_name,
                                             name='project_name') 
              
        self.project_location = _validate_string(arg=project_location,
                                                 name='project_location') 
        
        self.license_name = _validate_string(arg=license_name,
                                             name='license_name')  
              
        if isinstance(crs, (str, pyproj.crs.crs.CRS)):
            self.crs = crs                                             
        else:
            raise TypeError('The CRS must be provided as string or pyproj ' \
                            'CRS object')