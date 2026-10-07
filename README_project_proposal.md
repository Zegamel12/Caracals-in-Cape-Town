_Geoscripting Project Proposal_

Challenge 5:

'To what extend does a medium-sized predator care about human activity?'

Team name: ABC123

Team members: Joep van Dongen, Jerom den Rooijen, Silke Zeeuwen

Topic chosen: Challenge #5

Table of contents

[1\. Objective and research questions 3](#_Toc241682645)

[2\. Data 4](#_Toc241682646)

[3\. Methods 5](#_Toc241682647)

[4\. Reproducibility and efficiency 8](#_Toc241682648)

[5\. Expected output 9](#_Toc241682649)

# Objective and research questions

In line of the project for the course Geoscripting given at Wageningen University and Research the following research questions are formulated below. The goal of this project is to demonstrate the scripting skills of the authors that they learned during this course.

Main research question:

To answer the main research question, the following questions are to be answered in advance:

- Do caracals move at different speeds when they are close to roads compared with when they are farther from roads, potentially indicating a behavioural response to roads?
- Does the relationship between movement, speed and distance to roads differ between urban and wildland-dominated areas?
- Does the relationship between movement speed and distance to roads differ between daytime and nighttime?
- Do caracals show different levels of road proximity between urban and wildland-dominated areas and between daytime and nighttime?

# Data

To answer the research questions the following datasets will be used:

- Main dataset – GPS of caracals \[[LINK](https://www.movebank.org/cms/webapp?gwt_fragment=page%3Dstudies%2Cpath%3Dstudy1832666571) \]
  - Citation: Serieys LEK, Bishop JM, Rogan MS, Smith JA, Suraci JP, O'Riain MJ, Wilmers CC. 2023. Anthropogenic activities and age class mediate carnivore habitat selection in a human-dominated landscape. iScience. 26(7):107050. <https://doi.org/10.1016/j.isci.2023.107050>
    - GPS data of 27 caracals, period: 2014-2017, area: Cape town.
    - Available as .csv file and thus easily added to R and Python. File size: 10 mb, free to download. Also available through the API.
    - Dataset confirmed to be usable.
- Road network - OpenStreetMap \[[LINK](https://www.openstreetmap.org/)\]
  - Accessible directly in Python through packages like Pyrosm and OSMnx.
  - Extract only for extent of our research area.
  - Dataset confirmed to be usable.
- Urban boundary layers - \[[LINK](https://figshare.com/articles/dataset/Mapping_global_urban_boundaries_from_the_global_artificialimpervious_area_GAIA_data/32083476)\]
  - Citation: Li, Xuecao; Geng, Mengqing; Gong, Peng; Zhou, Yuyu (2026). Mapping global urban boundaries from the global artificial impervious area (GAIA) data. <https://doi.org/10.6084/m9.figshare.32083476.v1>
    - Global city/town boundary dataset, 2025. Free downloadable 160 mb _.shp_ file.
    - Clip to extent of our study area.
    - Dataset confirmed to be usable.
- Alternative: In Python, use OSMnx package which will use Geopandas and Openstreetmap to download boundaries. Free and openly available, allows for in script data retrieval. Package documentation: [OSMnx 2.1.1 documentation](https://osmnx.readthedocs.io/en/stable/index.html)

# Methods

Due to the complexity and variability of the project it is important that the methods that will be used are clear to an extent. The project methods will mainly contain of code using the program Python3.14.7 in Positron. A crucial part of the code will be the packages. Therefore, a clear overview of the workflow estimation and the packages is available below.

Workflow estimation:

- 1. Loading all data and packages, setting up a right project structure.
     - GPS data download by HTTP requests to webservice _Movebank REST API_ with import of **_requests_**_._
     - Data will be read and cleaned with usage of **_pandas_.**
     - After cleanup, longitude and latitude columns to be converted into point geometries with import of **_geopandas_**.
     - Reprojection of data in _WGS84_ to _UTM zone 34S_ also with **_geopandas/pyproj_**. This way distances can be calculated in metres.
  2. Setting up extent to delineate the area of GPS data for limiting dataset sizes.
     - - Reuse of _geopandas_ for writing a buffered bounding box based on the extent of acquired GPS data.
         - Reuse of _geopandas/pyproj_ for reprojecting the bounding box into _WGS84,_ since importing with _UTM zone 34S_ is not possible for _OSM_.
  3. Loading different datasets based on the set extent of research area.
     - Roads including road types, and other public data like for example landuse, are to be downloaded from _OpenStreetMap_ with import of **_osmnx_**.
       - Reuse of _geopandas/pyproj_ for converting OSM data into _UTM zone 34S_ as stated in step 1.
     - If landuse map of _OpenStreetMap_ is not sufficient for landuse differentiation on smaller scales, landuse can be differentiated with **_rasterio_** through importing satellite data with _requests_.
  4. Receiving and binding x/y coordinates, create a burst id to detect continuous GPS signals per individual.
     - GPS points are to be turned into trajectories per individual caracal. Differentiating trajectories into bursts when interval between measurements exceeds, a to be determined, time frame. This is to be done with import of **_movingpandas_**.
       - Reuse of _pandas_ and _geopandas_ for data reading, cleaning and writing.
  5. Visualize animal movements in map, with added temporal element. (animated)
     - Visualization of trajectories through time with **_plotly_**. With _plotly_ the map can become interactive. Time can be 'played' or 'paused' and areas can be zoomed into. In our tutorials folium was used, but for our project _plotly_ seems more capable, since it can be directly integrated for our interactive web app, see step 12.
       - Reuse of _movingpandas_ and _geopandas_ for input of data points and trajectories.
  6. Compute distances between closest road and animals for each GPS point.
     - - Reuse of _geopandas_ to calculate distances from GPS points to near roadlines.
         - Reuse of _pandas_ for creating classes of calculated distances for improved visualization in following steps.
  7. Compute movement speed based on distances between points and time interval.
     - - Reuse of _movingpandas_ to calculate distance and time between steps within a trajectory.
  8. Compare speed vs distance to road, to say something about avoidance behaviour.
     - To validate and verify relations within our calculated data we use **_statsmodels._**
       - Reuse of _pandas_ for summarizing results per individual caracal.
  9. Visualise results
     - With **_matplotlib_** graphs will be made of speed vs. the distance to road.
       - Reuse _geopandas_ and _plotly_ for making these graphs and maps interactive to be used in step 12.
  10. Make a time-based subset (day vs night). See if there are any differences between subsets. ,
      - To calculate sunrise and sunset conditions for GPS points a package named **_astral_** will be imported. Points can then be labelled with section of daytime or nighttime.
        - Reuse of _pandas_ to split this new day and night data into subsets.
        - Reuse of _statsmodels_ to test speed vs. distance relationship based on daytime or nighttime values.
        - Reuse _matplotlib_ and _plotly_ for visualization as stated in previous steps.
  11. Make area-based subsets (urban vs. nature). See if there are any differences between subsets.
      - - Reuse of _geopandas_ to label objects as urban or wildland.
          - Reuse of _pandas_ to split data into subset.
          - Reuse of statsmodels to calculate speed vs. distance relationship based on area of presence.
          - Reuse _matplotlib_ and _plotly_ for visualization as stated in previous steps.
  12. Interactive dashboard
      - Use of new package **streamlit** to build a python web app. Integrating all previously made calculations and visualizations into an interactive dashboard.
        - Reuse of _plotly_ for visualization in web app.

# Reproducibility and efficiency

To ensure reproducibility of this project, the following goals are adhered to. First, it is important that the script contains clear instructions and textual headings for the sake of clarity. This also includes the use of logical folder system inside the repository. Due to the complexity and number of variables the functions that will be used should be reusable. This can be done with functions that:

- Defines the study area so no unnecessary data will be downloaded (e.g. bbox function)
- Uses the same analytic techniques for the study areas
- Prepares raster data
- Automatically processes multiple files
- Calculates statistics
- Executes classifications
- Exports results
- Automatically produces maps

These functions will be written in designated files with clear written instructions. It will also be considered that these functions should be written in a way that makes them reproducible for other datasets or study areas. To further ensure the reproducibility there should be no pathways to personal computers, an automatic download of the data if possible, documented settings, separate input and output, and a README with clear instructions.

To ensure efficiency the code needs to be suitable to process spatial data and be as short as possible to the capabilities of the authors.

# Expected output

The final deliverables are a reproducible Python script containing the complete spatial analysis pipeline. In addition, an interactive Streamlit dashboard will be made to visualize these results. The visualisation will provide an overview of how the animals move through space and time. Showing the differences in movement behaviour between urban and non-urban areas and between day and night, all in relation to the distance from roads. Basic statistical analyses will be done to verify the significance of the observed differences and relations.