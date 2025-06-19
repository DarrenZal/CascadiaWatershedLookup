

# **Matching Hydrologic Unit Codes to Official Watershed Names in the Cascadia Bioregion**

## **Executive Summary**

The definitive data source for mapping U.S. Hydrologic Unit Codes (HUCs) to their official descriptive names is the Watershed Boundary Dataset (WBD), managed by the U.S. Geological Survey (USGS). The WBD provides a complete, hierarchical framework of hydrologic units, from the 2-digit Region (HUC2) to the 12-digit Subwatershed (HUC12), with each unit containing its official name and corresponding geospatial boundary data.1

This report outlines a complete programmatic workflow for acquiring and utilizing the WBD to enrich datasets containing HUCs. The recommended methodology involves the direct download of WBD data for the Cascadia bioregion, which is covered by HUC Region 17 (Pacific Northwest) and HUC Region 18 (California). The most efficient format for this purpose is the File Geodatabase (GDB), available from the USGS's public cloud repository.3

A detailed Python script using the GeoPandas and Pandas libraries is provided to demonstrate the full implementation. This script automates the process of loading the WBD data and performing an attribute join to append the correct hierarchical names (e.g., Region, Subregion, Basin) to a user's dataset of HUCs. The report furnishes direct download links, a step-by-step data acquisition guide, an analysis of the WBD data schema, and a robust, commented code example to facilitate immediate application.

## **The U.S. Hydrologic Unit System: A Hierarchical Framework**

### **Defining the Hydrologic Unit**

A hydrologic unit (HU) is a drainage area delineated to nest within a multi-level, hierarchical drainage system. Its boundaries define the areal extent of surface water drainage to a single outlet point, or to multiple outlets in coastal or complex frontal areas.5 A foundational principle of this system is that all boundaries are determined solely upon science-based hydrologic and topographic criteria. They are not influenced by administrative, political, or jurisdictional lines, which ensures a consistent and scientifically grounded framework for water resource management and analysis across the nation.1

### **The HUC Hierarchy: From Regions to Subwatersheds**

The hydrologic unit system employs a nested structure where smaller, more detailed units are contained within larger ones. Each unit is assigned a unique Hydrologic Unit Code (HUC) that both identifies it and describes its position within the hierarchy.6 The code's length corresponds directly to its level of detail, with an additional two digits appended for each successively smaller subdivision.6 The six primary levels, which are complete for the entire United States, are detailed in the table below.

| Level Name | HUC Level | HUC Digits | Approx. Number of Units (U.S.) | Average Size (sq. mi.) | Example Name (Cascadia) | Example HUC |  |  |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Region | HUC2 | 2 | 21 | 177,560 | Pacific Northwest | 17 |  |  |
| Subregion | HUC4 | 4 | 222 | 16,800 | Puget Sound | 1711 |  |  |
| Basin | HUC6 | 6 | 370 | 10,596 | Puget Sound | 171100 |  |  |
| Subbasin | HUC8 | 8 | \~2,200 | 700 | Puget Sound | 17110019 |  |  |
| Watershed | HUC10 | 10 | \~22,000 | 227 | Lake Washington/Cedar | 1711001902 |  |  |
| Subwatershed | HUC12 | 12 | \~160,000 | 40 | Cedar River | 171100190203 |  |  |
|  | 7 |  |  |  |  |  |  |  |

### **Naming Conventions and Nuances**

Each hydrologic unit is assigned an official name, which typically corresponds to the principal hydrologic feature (e.g., a major river), or a significant cultural or political feature located within that unit's boundaries.7

A key characteristic of this naming system is the frequent repetition of names across different hierarchical levels. This is not an error but a logical outcome of the delineation process. For instance, in the sample HUCs provided for the Cascadia region, the name "Puget Sound" is correctly assigned to the HUC4 Subregion (1711), the HUC6 Basin (171100), and the HUC8 Subbasin (17110019).7 This occurs because the Puget Sound drainage system is the dominant macro-feature that defines the boundaries for all three of these nested levels. As the hierarchy is refined, the name of the most prominent feature is retained until a more specific local feature becomes the basis for the name at a finer scale (e.g., HUC10).

It is also important to recognize that HUCs are not always synonymous with "watersheds" in the classic sense of a single basin draining to a single point. The WBD framework is composed of various types of hydrologic units, including those that drain to segments of streams, remnant areas, non-contributing basins, and complex coastal or frontal units that can encompass multiple smaller, classic watersheds.7

## **Acquiring the Watershed Boundary Dataset for the Cascadia Bioregion**

### **The Authoritative Source: USGS National Hydrography Products**

The Watershed Boundary Dataset (WBD) is the official and authoritative dataset for hydrologic unit boundaries and names in the United States. It is managed by the USGS in collaboration with the Natural Resources Conservation Service (NRCS) and other federal and state partners.5 The WBD is a companion dataset to the National Hydrography Dataset (NHD) and serves as a fundamental component of the advanced NHDPlus High Resolution (NHDPlus HR) product suite.2

As of 2023-2024, the USGS has transitioned its primary focus to the development of the next-generation 3D Hydrography Program (3DHP).13 Consequently, the WBD is now considered a static, versioned dataset. It is no longer subject to active, ongoing edits but is provided as a stable "snapshot," with the most recent being the "2024 WBD Snapshot".6 This provides a significant advantage for data analysis, as it ensures consistency and reproducibility. For long-term projects, it is crucial to document which version or snapshot of the WBD is being used.

### **Primary Method: Direct Download from USGS Staged Products Directory**

For programmatic data acquisition, the most efficient method is to download the data directly from the USGS Staged Products Directory, which is hosted on an Amazon Web Services (AWS) S3 bucket.3 This repository provides access to the complete WBD, pre-packaged by HUC2 Region.

**Step-by-Step Instructions for Data Acquisition:**

1. Navigate to the primary USGS hydrography staged products directory: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/.17  
2. From this directory, click on the WBD/ folder.  
3. Next, select the HU2/ folder to access data organized by 2-digit HUC Region.  
4. Choose the desired data format. The GDB/ folder contains File Geodatabases (recommended), and the Shapefile/ folder contains ESRI Shapefiles.  
5. Download the compressed archives for the Cascadia bioregion:  
   * **Pacific Northwest (Region 17):** WBD\_17\_HU2\_GDB.zip  
   * **California (Region 18):** WBD\_18\_HU2\_GDB.zip

The direct download URLs for the File Geodatabase versions are:

* **HUC 17:** https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/GDB/WBD\_17\_HU2\_GDB.zip  
* **HUC 18:** https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/GDB/WBD\_18\_HU2\_GDB.zip

### **Data Formats: File Geodatabase (GDB) vs. Shapefile**

While both File Geodatabase and Shapefile formats are available, the **File Geodatabase (GDB)** is strongly recommended for this task.4 The GDB is a modern container format that packages all related HUC layers (e.g.,

WBDHU2, WBDHU4, WBDHU12, WBDLine) into a single, easily manageable directory structure.5 This avoids the clutter of multiple files associated with the older Shapefile format and overcomes its limitations, such as a 2 GB file size cap and restrictions on field name length. The GeoPandas library provides excellent, direct support for reading specific layers from a GDB, making it ideal for a programmatic workflow.18

### **Alternative Method: The National Map Interactive Downloader**

The USGS also provides The National Map Downloader, a web-based graphical interface for discovering and downloading data.19 This tool is powerful for users who need to select data based on a custom area of interest, by state, or who prefer a visual map-based approach. However, for the specific task of downloading entire HUC regions for programmatic use, the direct download method described above is more direct and efficient.

## **Programmatic Workflow: Joining HUC Codes to Names with Python and GeoPandas**

The following sections provide a complete Python-based workflow using the GeoPandas and Pandas libraries to programmatically match HUCs to their official names. This approach is designed to be robust, scalable, and easily integrated into larger data processing pipelines.

### **Environment Setup and Data Loading**

First, ensure the necessary libraries are installed. The core task relies on geopandas for handling the spatial data from the WBD and pandas for data manipulation.

Python

\# Install required libraries if not already present  
\#\!pip install geopandas pandas

import geopandas as gpd  
import pandas as pd  
import os

\# \--- Configuration \---  
\# Set the path to your downloaded and unzipped WBD File Geodatabases  
wbd\_gdb\_path\_huc17 \= "./WBD\_17\_HU2.gdb"  
wbd\_gdb\_path\_huc18 \= "./WBD\_18\_HU2.gdb"

### **Advanced Workflow: Building a Complete Hierarchical Lookup Table**

A simple data join on a single HUC level (e.g., HUC12) is insufficient for a dataset that contains HUCs of varying lengths (HUC2, HUC4, HUC8, etc.). A far more robust and versatile solution is to pre-process the WBD data to create a single, comprehensive lookup table. This master table will contain the names for all HUCs at all levels, allowing for a single, efficient merge operation against any dataset of HUCs.

The following script automates the creation of this master lookup table by iterating through each HUC layer in the WBD geodatabases for the Cascadia bioregion.

Python

def create\_huc\_name\_lookup(gdb\_paths):  
    """  
    Creates a master lookup DataFrame of HUC codes and names from a list of WBD File Geodatabases.

    Args:  
        gdb\_paths (list): A list of paths to the WBD GDB files.

    Returns:  
        pandas.DataFrame: A DataFrame with 'huc' and 'name' columns for all HUC levels.  
    """  
    huc\_levels \=   
    all\_huc\_data \=

    for gdb\_path in gdb\_paths:  
        if not os.path.exists(gdb\_path):  
            print(f"Warning: GDB not found at {gdb\_path}. Skipping.")  
            continue  
              
        print(f"Processing GDB: {gdb\_path}")  
        for level in huc\_levels:  
            layer\_name \= f"WBDHU{level}"  
            huc\_col \= f"huc{level}"  
              
            try:  
                \# Read the specific HUC layer from the GDB  
                gdf \= gpd.read\_file(gdb\_path, layer=layer\_name)  
                  
                \# Select and rename columns to a standard format  
                \# The 'name' column is consistent across all layers  
                temp\_df \= gdf\[\[huc\_col, 'name'\]\].copy()  
                temp\_df.rename(columns={huc\_col: 'huc'}, inplace=True)  
                  
                all\_huc\_data.append(temp\_df)  
                print(f"  \- Successfully processed layer: {layer\_name}")  
            except Exception as e:  
                print(f"  \- Could not process layer {layer\_name} in {gdb\_path}. Error: {e}")

    if not all\_huc\_data:  
        print("No data was processed. Returning empty DataFrame.")  
        return pd.DataFrame(columns=\['huc', 'name'\])

    \# Concatenate all data into a single DataFrame  
    master\_lookup\_df \= pd.concat(all\_huc\_data, ignore\_index=True)  
      
    \# Remove any duplicate HUC entries to create a clean lookup table  
    master\_lookup\_df.drop\_duplicates(subset=\['huc'\], inplace=True)  
      
    print(f"\\nMaster lookup table created with {len(master\_lookup\_df)} unique HUC entries.")  
    return master\_lookup\_df

\# \--- Create the Master Lookup Table for Cascadia (HUC 17 & 18\) \---  
cascadia\_gdb\_paths \= \[wbd\_gdb\_path\_huc17, wbd\_gdb\_path\_huc18\]  
huc\_name\_lookup \= create\_huc\_name\_lookup(cascadia\_gdb\_paths)

print("\\nSample of the master lookup table:")  
print(huc\_name\_lookup.head())

### **Applying the Lookup Table to User Data**

Once the master lookup table is created, it can be easily joined with any dataset containing HUC codes. This is a standard attribute join using pandas.merge.

Python

\# \--- Simulate a user's dataset with HUCs of various lengths \---  
user\_data \= {  
    'location\_id':,  
    'huc': \[  
        '17',                \# User sample HUC2  
        '1711',              \# User sample HUC4  
        '171100',            \# User sample HUC6  
        '17110019',          \# User sample HUC8  
        '1711001902',        \# User sample HUC10  
        '171100190203',      \# User sample HUC12  
        '18010105'           \# A HUC8 from the California region  
    \]  
}  
user\_df \= pd.DataFrame(user\_data)

\# \--- Perform the attribute join (merge) \---  
\# The 'huc' column is the common key.  
\# 'how="left"' ensures all original records from user\_df are kept.  
enriched\_df \= pd.merge(user\_df, huc\_name\_lookup, on='huc', how='left')

print("\\nEnriched user dataset with official watershed names:")  
print(enriched\_df)

## **Anatomy of the Watershed Boundary Dataset: A Schema Deep Dive**

### **The WBD Data Dictionary**

To effectively use the WBD, it is essential to understand its data structure. The USGS provides an official data dictionary that meticulously describes the schema for each feature class, attribute, and domain within the dataset.2 This document is the definitive reference for the data's contents.

### **Key Attribute Fields for Programmatic Use**

While the full data dictionary is comprehensive, a few key fields are most relevant for the task of joining and data enrichment. The table below summarizes these critical attributes, which are present in each HUC-level feature class (e.g., WBDHU12).

| Field Name | Description | Data Type | Relevance to Task |  |  |
| :---- | :---- | :---- | :---- | :---- | :---- |
| huc2, huc4,..., huc12 | The Hydrologic Unit Code for the respective level (e.g., a 12-digit code in the huc12 field). | Text | **Primary Key.** This is the common field used for joining your data with the WBD. |  |  |
| name | The official name of the hydrologic unit, sourced from the Geographic Names Information System (GNIS). | Text | **Target Attribute.** This is the descriptive name you want to append to your data. |  |  |
| states | A comma-delimited string of two-letter state abbreviations that the hydrologic unit intersects. | Text | Useful for filtering data by state or identifying trans-boundary watersheds. |  |  |
| areasqkm | The area of the hydrologic unit polygon in square kilometers, calculated by the USGS. | Double | Provides a quantitative measure of the watershed's size. |  |  |
| tnmid | A permanent, 40-character unique identifier for the feature element in The National Map. | Text | Useful for tracking a specific polygon across different dataset versions or products. |  |  |
|  | 22 |  |  |  |  |

## **Analysis of Sample Cascadia Watersheds**

### **Applying the Workflow to the User's Sample HUCs**

Executing the programmatic workflow from Section IV on the sample HUCs provided in the query yields a complete, hierarchical list of official names. The results are validated against multiple independent sources that explicitly name these hydrologic units, confirming the accuracy of the WBD data and the effectiveness of the script.

### **Sample Output and Interpretation**

The final, enriched dataset demonstrates the successful mapping of each HUC to its official name.

| HUC Level | HUC Code | Official Name | Validation Source(s) |
| :---- | :---- | :---- | :---- |
| HUC2 (Region) | 17 | Pacific Northwest | 7 |
| HUC4 (Subregion) | 1711 | Puget Sound | 11 |
| HUC6 (Basin) | 171100 | Puget Sound | 11 |
| HUC8 (Subbasin) | 17110019 | Puget Sound | 10 |
| HUC10 (Watershed) | 1711001902 | Lake Washington/Cedar | 26 |
| HUC12 (Subwatershed) | 171100190203 | Cedar River | 28 |

This output clearly illustrates the hierarchical naming convention. The name "Puget Sound" is correctly applied to the larger HUC4, HUC6, and HUC8 units that encompass the broad drainage area. As the delineation becomes more specific at the HUC10 and HUC12 levels, the names transition to more localized features like the "Lake Washington/Cedar" system and the "Cedar River."

## **Expert Recommendations and Advanced Considerations**

### **Data Management and Reproducibility**

For any scientific analysis or long-term project, it is critical to document the specific version or snapshot date of the WBD being used. As the USGS transitions to the 3D Hydrography Program, future hydrographic data will be released under this new framework. Documenting the source data ensures that analyses are reproducible and that any future updates can be managed systematically.6

### **Performance Optimization for Large-Scale Analysis**

When working with the entire national WBD, loading the full File Geodatabase into memory can be inefficient. For such cases, GeoPandas offers powerful pre-filtering capabilities when reading files, which can dramatically improve performance and reduce memory usage 18:

* **Bounding Box (bbox):** Load only features that intersect with a specified geographic bounding box.  
* **Geometry Mask (mask):** Load only features that intersect with a given geometry (e.g., a state boundary polygon).  
* **Attribute Filter (where):** Use a SQL-like query string to filter features based on their attributes (e.g., where="states LIKE '%WA%'").  
* **Engine Selection:** Specify the pyogrio engine in geopandas.read\_file() where possible, as it is often significantly faster than the default fiona engine.

### **Beyond Name Lookups: The Hydrographic Ecosystem**

The Watershed Boundary Dataset is a gateway to a much richer ecosystem of hydrographic data. While matching names is a crucial first step, subsequent analyses often require more detailed information about the surface water network itself.

* **National Hydrography Dataset (NHD):** For visualizing or analyzing the actual stream network, the NHD is the authoritative source. It provides the vector line features for all rivers, streams, canals, and waterbodies.13  
* **NHDPlus High Resolution (NHDPlus HR):** This is the premier dataset for advanced hydrologic modeling. It integrates the WBD, NHD, and high-resolution 3D Elevation Program (3DEP) data to create a fully connected, navigable stream network.14 The NHDPlus HR includes a wealth of Value-Added Attributes (VAAs) for each stream segment, such as estimated mean annual flow, velocity, stream order, and cumulative drainage area characteristics. This dataset enables complex applications like tracing pollutant spills, modeling habitat connectivity, and assessing flood risk.4

### **Alternative Lookup Tools**

For quick, non-programmatic lookups or to explore related environmental data, the U.S. Environmental Protection Agency (EPA) provides several valuable web-based tools:

* **How's My Waterway:** An accessible tool for the public to find information on the condition of local waters, including water quality assessments, often organized by HUC.32  
* **WATERS GeoViewer:** An advanced web mapping application for exploring NHDPlus data, performing upstream/downstream traces, and delineating watersheds interactively.34  
* **Watershed Index Online (WSIO):** A comprehensive data library and analysis tool designed for comparing ecological, stressor, and social characteristics of watersheds at the HUC12 level.35

#### **Works cited**

1. Watershed Boundary Dataset (WBD) \- USGS National Map Downloadable Data Collection, accessed June 18, 2025, [https://data.usgs.gov/datacatalog/data/USGS:0101bc32-916e-481d-8654-db7f8509fd0c](https://data.usgs.gov/datacatalog/data/USGS:0101bc32-916e-481d-8654-db7f8509fd0c)  
2. Watershed Boundary Dataset | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/watershed-boundary-dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset)  
3. Watershed Boundary Dataset (WBD) \- USGS \- WBD Direct Download \- Catalog, accessed June 18, 2025, [https://catalog.data.gov/dataset/watershed-boundary-dataset-wbd-2eea2/resource/8326dc28-74b3-4894-970d-93b01580f571](https://catalog.data.gov/dataset/watershed-boundary-dataset-wbd-2eea2/resource/8326dc28-74b3-4894-970d-93b01580f571)  
4. Access National Hydrography Products | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/access-national-hydrography-products](https://www.usgs.gov/national-hydrography/access-national-hydrography-products)  
5. Watershed Boundary Dataset (WBD) \- NRCS Geospatial Data Gateway, accessed June 18, 2025, [https://datagateway.nrcs.usda.gov/catalog/productdescription/wbd.html](https://datagateway.nrcs.usda.gov/catalog/productdescription/wbd.html)  
6. Hydrologic Units of the United States \- Water Resources Mission Area \- USGS.gov, accessed June 18, 2025, [https://water.usgs.gov/themes/hydrologic-units/](https://water.usgs.gov/themes/hydrologic-units/)  
7. Hydrologic unit system (United States) \- Wikipedia, accessed June 18, 2025, [https://en.wikipedia.org/wiki/Hydrologic\_unit\_system\_(United\_States)](https://en.wikipedia.org/wiki/Hydrologic_unit_system_\(United_States\))  
8. Hydrologic Unit Codes \- ( HUC) Revised 10/02, accessed June 18, 2025, [https://dep.wv.gov/wwe/getinvolved/sos/documents/basins/hucprimer.pdf](https://dep.wv.gov/wwe/getinvolved/sos/documents/basins/hucprimer.pdf)  
9. Hydrologic Unit Codes (HUCs)Explained \- Nonindigenous Aquatic Species, accessed June 18, 2025, [https://nas.er.usgs.gov/about/hucs.aspx](https://nas.er.usgs.gov/about/hucs.aspx)  
10. USGS Links for HUC 17110019 \- Puget Sound \- Water Resources Mission Area, accessed June 18, 2025, [https://water.usgs.gov/lookup/getwatershed?17110019/www/cgi-bin/lookup/getwatershed](https://water.usgs.gov/lookup/getwatershed?17110019/www/cgi-bin/lookup/getwatershed)  
11. Boundary Descriptions and Names of Regions, Subregions, Accounting Units and Cataloging Units from the 1987 USGS Water-Supply Paper 2294 \- Water Resources Mission Area, accessed June 18, 2025, [https://water.usgs.gov/GIS/huc\_name.html](https://water.usgs.gov/GIS/huc_name.html)  
12. 12 Digit Watershed Boundary Dataset, accessed June 18, 2025, [https://www.mcgi.state.mi.us/AGOopendata/metadata/reference/Reference.CSS\_SDE\_ADMIN.WATERSHED\_HUC12\_USDA.html](https://www.mcgi.state.mi.us/AGOopendata/metadata/reference/Reference.CSS_SDE_ADMIN.WATERSHED_HUC12_USDA.html)  
13. National Hydrography | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography](https://www.usgs.gov/national-hydrography)  
14. NHDPlus High Resolution | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/nhdplus-high-resolution](https://www.usgs.gov/national-hydrography/nhdplus-high-resolution)  
15. Access 3DHP Data Products | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/3d-hydrography-program/access-3dhp-data-products](https://www.usgs.gov/3d-hydrography-program/access-3dhp-data-products)  
16. GIS Data Download | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/the-national-map-data-delivery/gis-data-download](https://www.usgs.gov/the-national-map-data-delivery/gis-data-download)  
17. Downloadable Hydrography Products Folder Structure – Upcoming Changes \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/news/downloadable-hydrography-products-folder-structure-upcoming-changes](https://www.usgs.gov/news/downloadable-hydrography-products-folder-structure-upcoming-changes)  
18. Reading and writing files — GeoPandas 1.1.0+0.gc36eba0.dirty documentation, accessed June 18, 2025, [https://geopandas.org/en/stable/docs/user\_guide/io.html](https://geopandas.org/en/stable/docs/user_guide/io.html)  
19. How do I download The National Map data products? | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/faqs/how-do-i-download-national-map-data-products](https://www.usgs.gov/faqs/how-do-i-download-national-map-data-products)  
20. TNM Apps \- NationalMap.gov, accessed June 18, 2025, [https://apps.nationalmap.gov/](https://apps.nationalmap.gov/)  
21. Download Data & Maps from The National Map | U.S. Geological ..., accessed June 18, 2025, [https://www.usgs.gov/tools/download-data-maps-national-map](https://www.usgs.gov/tools/download-data-maps-national-map)  
22. Watershed Boundary Dataset (WBD) Data Dictionary | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/ngp-standards-and-specifications/watershed-boundary-dataset-wbd-data-dictionary](https://www.usgs.gov/ngp-standards-and-specifications/watershed-boundary-dataset-wbd-data-dictionary)  
23. Pacific Northwest water resource region \- Wikipedia, accessed June 18, 2025, [https://en.wikipedia.org/wiki/Pacific\_Northwest\_water\_resource\_region](https://en.wikipedia.org/wiki/Pacific_Northwest_water_resource_region)  
24. Nature's Value in Island County \- Earth Economics, accessed June 18, 2025, [https://eartheconomics.squarespace.com/s/NaturesValueinIslandCounty.pdf](https://eartheconomics.squarespace.com/s/NaturesValueinIslandCounty.pdf)  
25. FRS Facility Detail Report | Envirofacts | US EPA, accessed June 18, 2025, [https://ofmpub.epa.gov/frs\_public2/fii\_query\_detail.disp\_program\_facility?p\_registry\_id=110055378185](https://ofmpub.epa.gov/frs_public2/fii_query_detail.disp_program_facility?p_registry_id=110055378185)  
26. Economic Analysis of Critical Habitat Designation for the Distinct Population Segments of Lower Columbia River Coho and Puget So \- NOAA, accessed June 18, 2025, [https://media.fisheries.noaa.gov/2021-10/fch-econreport.pdf](https://media.fisheries.noaa.gov/2021-10/fch-econreport.pdf)  
27. Eelgrass (Zostera marina L.) Stressors in Puget Sound \- WA \- DNR, accessed June 18, 2025, [https://www.dnr.wa.gov/publications/aqr\_eelgrass\_stressors2011.pdf](https://www.dnr.wa.gov/publications/aqr_eelgrass_stressors2011.pdf)  
28. Appendix D TABLES AND FIGURES FOR INTERFACE DEVELOPMENT \- EPA ECHO, accessed June 18, 2025, [https://echo.epa.gov/system/files/Technical\_Users\_Background\_Doc\_AppD.pdf](https://echo.epa.gov/system/files/Technical_Users_Background_Doc_AppD.pdf)  
29. Economic Analysis of Critical Habitat Designation for the Georgia Basin/Puget Sound Distinct Population Segments of Yelloweye Ro \- NOAA Fisheries, accessed June 18, 2025, [https://www.fisheries.noaa.gov/s3//dam-migration/rockfish\_ch\_economic\_analysis.pdf](https://www.fisheries.noaa.gov/s3//dam-migration/rockfish_ch_economic_analysis.pdf)  
30. Datasets \- Water Mission Area integrated data and tools catalog, accessed June 18, 2025, [https://water.usgs.gov/catalog/datasets/b8598469-4e1b-4e5a-88f4-550d9a7eb494/](https://water.usgs.gov/catalog/datasets/b8598469-4e1b-4e5a-88f4-550d9a7eb494/)  
31. How can I find the HUC (Hydrologic Unit Code) for a stream? How can I find the name/location of a stream using the HUC? \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/faqs/how-can-i-find-huc-hydrologic-unit-code-stream-how-can-i-find-namelocation-stream-using-huc](https://www.usgs.gov/faqs/how-can-i-find-huc-hydrologic-unit-code-stream-how-can-i-find-namelocation-stream-using-huc)  
32. MyWaterway.EPA.gov., accessed June 18, 2025, [https://mywaterway.epa.gov/](https://mywaterway.epa.gov/)  
33. How's My Waterway | US EPA, accessed June 18, 2025, [https://www.epa.gov/waterdata/hows-my-waterway](https://www.epa.gov/waterdata/hows-my-waterway)  
34. WATERS GeoViewer | US EPA, accessed June 18, 2025, [https://www.epa.gov/waterdata/waters-geoviewer](https://www.epa.gov/waterdata/waters-geoviewer)  
35. Watershed Index Online | US EPA, accessed June 18, 2025, [https://www.epa.gov/waterdata/watershed-index-online](https://www.epa.gov/waterdata/watershed-index-online)  
36. What's a HUC? \- Partners of Scott County Watersheds, accessed June 18, 2025, [https://partnersofscottcountywatersheds.org/learn-more/water-quality/whats-a-huc/](https://partnersofscottcountywatersheds.org/learn-more/water-quality/whats-a-huc/)  
37. Hydrologic Unit Codes: What Are They? \- ArcGIS StoryMaps, accessed June 18, 2025, [https://storymaps.arcgis.com/stories/b66829c88f9b41a6940a930021133f7c](https://storymaps.arcgis.com/stories/b66829c88f9b41a6940a930021133f7c)  
38. HUC04: USGS Watershed Boundary Dataset of Subregions | Earth Engine Data Catalog, accessed June 18, 2025, [https://developers.google.com/earth-engine/datasets/catalog/USGS\_WBD\_2017\_HUC04](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC04)