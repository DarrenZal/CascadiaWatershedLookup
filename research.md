# **A Technical Blueprint for Implementing a Cross-Border Watershed Identification Service for the Cascadia Bioregion**

## **Executive Summary**

This report provides a comprehensive technical blueprint for developing a software function capable of identifying the specific watershed and sub-watershed for any given location within the Cascadia bioregion. The function is designed to accept a user-provided address or postal code, which spans both the United States and Canada, and return detailed, hierarchical watershed information suitable for mapping and community organization.

The primary challenge addressed is the harmonization of disparate national hydrographic datasets from the United States and Canada. The U.S. relies on the standardized Watershed Boundary Dataset (WBD) with its Hydrologic Unit Code (HUC) system, while Canada utilizes the Standard Drainage Area Classification (SDAC) and is transitioning from the National Hydro Network (NHN) to the more advanced Canadian Hydrospatial Network (CHN).

This document outlines a robust, offline-first architectural approach. It details a complete data processing pipeline to create a single, unified, and pre-processed geospatial data file covering the entire Cascadia bioregion. This approach involves:

1. Defining a precise, scientifically-backed operational boundary for Cascadia.  
2. Acquiring and processing authoritative watershed data from both U.S. and Canadian government sources.  
3. Harmonizing the different data schemas and hierarchical coding systems into a single, cohesive data model.  
4. Implementing a high-performance point-in-polygon query using this unified dataset.

The report concludes with a strong recommendation for this offline architecture due to its reliability, performance, and ability to guarantee complete coverage across the trans-national bioregion, a core requirement of the project. Detailed implementation guidance, including Python code examples using the GeoPandas library, is provided to enable direct execution of the proposed solution.

---

### **Part I: Foundational Concepts and Data Acquisition**

This part establishes the conceptual and data-driven foundation for the project. It defines the operational boundaries for the analysis and identifies the authoritative raw data required from both the United States and Canada to ensure comprehensive and accurate coverage.

#### **Section 1: Delineating "Cascadia" — An Operational Boundary for Analysis**

##### **1.1 The Bioregional Concept**

The Cascadia bioregion is not defined by conventional political lines but by the natural contours of the land and water. It is a "bio-cultural region" primarily delineated by the watersheds of the major river systems that define the Pacific Northwest, principally the Columbia, Fraser, and Snake Rivers.1 This concept extends from the Pacific coast eastward to the Continental Divide, and from Northern California to Southern Alaska, encompassing a vast and ecologically diverse area.1 The philosophy underpinning bioregionalism is the alignment of human activity, including cultural and political organization, with these natural ecological systems, with a core goal of promoting environmental stewardship.2 This principle makes a watershed-based data model the most appropriate and authentic foundation for this project.

##### **1.2 Selecting an Authoritative Boundary**

While the concept of Cascadia is fluid, a software application requires a fixed, machine-readable boundary to define its Area of Interest (AOI). Various maps and definitions exist, originating from different organizations and for different purposes, such as cultural identity, geological analysis of the Cascadia Subduction Zone, or economic planning.4 For a reproducible and scientifically grounded software project, a single, authoritative geospatial file must be selected.

The most suitable source identified is a feature layer titled "Cascadia Bioregion boundaries," developed by Dr. Aquila Flower's research group at Western Washington University (WWU).6 This dataset is explicitly documented as being delineated based on watershed boundaries, using publications from the Cascadia Institute as its primary reference.6 This methodology aligns perfectly with the project's core purpose. Using this layer provides a clear, citable, and scientifically defensible AOI, transforming the abstract idea of Cascadia into a concrete technical specification. This choice is fundamental, as it dictates the scope of all subsequent data acquisition and processing steps, directly impacting data storage requirements and computational workload.

##### **1.3 Acquiring the Boundary File**

The authoritative AOI is available as an ArcGIS Feature Service.6 While a direct download link for a specific format like a Shapefile, GeoJSON, or KML is not provided on the item's overview page 6, the data can be extracted. The metadata indicates the service was created from a Shapefile.6 Developers can access this data by:

* Using ArcGIS software (like ArcGIS Pro or ArcGIS Online) to connect to the Feature Service and export the layer to a desired format.  
* Programmatically querying the REST endpoint of the Feature Service to retrieve the polygon geometry, which can then be saved as a GeoJSON or other vector file.

**Table 1.1: Cascadia Bioregion Boundary Data Source Analysis**

| Source Name | Link/Reference | Format(s) | Description/Methodology | Recommendation |
| :---- | :---- | :---- | :---- | :---- |
| **Cascadia Bioregion Boundaries (WWU)** | ArcGIS Hub Item: c6497941559d433da98e286fb3f63551 6 | Feature Service (from Shapefile) | Delineated based on watershed boundaries defined by the Cascadia Institute. | **Recommended.** Most scientifically aligned with the project's goals. |
| **Sightline Institute Cascadia Map** | Sightline Institute Website 4 | PDF, Poster | A visual representation for advocacy and education. Not provided as a geospatial data file. | Not suitable for direct use. Good for conceptual reference. |
| **Cascadia Dept. of Bioregion Maps** | cascadiabioregion.org 3 | Image files (JPG, PNG) | High-resolution visual maps showing hydrology and ecoregions. Not provided as a geospatial data file. | Not suitable for direct use. Excellent for visualization context. |
| **Cascadia Subduction Zone Database** | USGS 10 | Various geospatial datasets | Defines the region based on tectonic plate geology. | Not suitable. Geologically focused, not watershed-focused. |

#### **Section 2: The U.S. Hydrological Data Framework: WBD and HUC**

##### **2.1 The Watershed Boundary Dataset (WBD)**

For the U.S. portion of Cascadia, the definitive data source is the Watershed Boundary Dataset (WBD). This is a national, seamless dataset maintained by the U.S. Geological Survey (USGS) in collaboration with the Natural Resources Conservation Service (NRCS) and other state and federal partners.11 The WBD defines the areal extent of surface water drainage based on scientific hydrologic principles, independent of administrative or political boundaries.11 It is delineated at a high resolution, typically a 1:24,000 map scale in the conterminous U.S., ensuring a fine level of detail suitable for this project's granularity requirements.11

##### **2.2 The Hydrologic Unit Code (HUC) System**

The WBD organizes the nation's watersheds into a nested, hierarchical system. Each drainage area, or Hydrologic Unit (HU), is assigned a unique Hydrologic Unit Code (HUC) that identifies its location and level within the hierarchy.14 This structure is fundamental to providing the multi-level watershed information requested by the user. The hierarchy is encoded directly into the digits of the code, allowing for straightforward programmatic parsing of a watershed's lineage.16 The standard levels are 13:

* **2-Digit HUC (HUC2):** Region (e.g., 17 for the Pacific Northwest)  
* **4-Digit HUC (HUC4):** Sub-region  
* **6-Digit HUC (HUC6):** Basin  
* **8-Digit HUC (HUC8):** Sub-basin (a very common unit for regional analysis) 16  
* **10-Digit HUC (HUC10):** Watershed  
* **12-Digit HUC (HUC12):** Sub-watershed (provides the fine granularity required)

For example, a HUC12 polygon with the code 170101010101 is nested within the HUC10 1701010101, which is within the HUC8 17010101, and so on. The WBD is complete for the entire U.S. to the 12-digit level.15

##### **2.3 WBD Data Acquisition**

The complete WBD can be downloaded as a national dataset from official government portals. The most common formats are ESRI File Geodatabase (FGDB) and Shapefile.12 Authoritative sources include:

* **The USGS National Map Download Viewer:** Provides access to the latest WBD data products.11  
* **NRCS Geospatial Data Gateway:** Offers WBD data and archives of national layers.12  
* **Direct S3 Bucket Access:** The USGS also provides direct download links to snapshots of the WBD in their public Amazon S3 buckets.19

For this project, downloading the national HUC12 polygon layer is the recommended starting point for the U.S. data.

#### **Section 3: The Canadian Hydrological Data Framework: SDAC and CHN**

##### **3.1 Canada's Evolving Hydrography**

The hydrographic data landscape in Canada is more complex than in the U.S. and is currently in a state of transition. For many years, the **National Hydro Network (NHN)** has been the standard national dataset.20 However, Natural Resources Canada (NRCan) is actively developing and rolling out its replacement: the

**Canadian Hydrospatial Network (CHN)**.22

The CHN represents a significant advancement, offering higher resolution, better alignment with elevation data (like LiDAR), and an analysis-ready data model with attributes designed for hydrologic modeling.22 However, the CHN is being rolled out progressively by geographic work units, and national coverage is not yet complete.22 This presents a notable challenge. A software solution that relies exclusively on the CHN risks having significant data gaps within the Canadian portion of Cascadia. The older NHN, while having a less advanced data model and lower resolution, offers more comprehensive national coverage.25 A robust implementation must therefore consider a hybrid strategy: prioritizing the use of CHN data where it is available and complete, but falling back to the NHN or high-quality provincial datasets to fill any gaps and ensure total coverage of the Cascadia AOI.

##### **3.2 The Standard Drainage Area Classification (SDAC)**

The Canadian analogue to the HUC system is the **Standard Drainage Area Classification (SDAC)**, managed by Statistics Canada.26 It is based on the drainage area framework established by the Water Survey of Canada (WSC) and provides a hierarchical system for statistical reporting.28 The SDAC hierarchy consists of three main levels 26:

* **Major Drainage Areas (MDAs):** The highest level, with 11 covering Canada (e.g., Code 08 for the Pacific drainage area).31  
* **Sub-Drainage Areas (SDAs):** The second level, with 164 across the country.  
* **Sub-Sub-Drainage Areas (SSDAs):** The finest level in the classification, with 978 covering the Canadian landmass.26

The coding system is alphanumeric. A four-character code identifies a unique SSDA, with the first two digits representing the parent MDA, the third letter representing the SDA, and the fourth letter representing the SSDA (e.g., 08GA).26

##### **3.3 The Canadian Hydrospatial Network (CHN) Data Model**

The new CHN is designed to be more feature-rich and analysis-ready than its predecessor. Its data model includes several key layers 23:

* flowlines: The linear network of rivers and streams.  
* waterbodies: Polygon features for lakes and reservoirs.  
* catchments: The fundamental drainage areas, analogous to a fine-level HUC. These are the key polygons for this project.  
* work\_units: The geographic tiles used for data production and distribution, which are often based on the WSC Sub-Sub-Drainage Areas.23

A critical feature for this project is that the CHN data model provides a bridge to the SDAC system. The work\_unit and other tables contain attributes that explicitly store the corresponding WSC/SDAC codes (wscmda, wscsda, wscssda) and names.23 This linkage is essential for the data harmonization process, allowing for the creation of a unified output that includes both the modern CHN identifiers and the established SDAC classification.

##### **3.4 Canadian Data Acquisition**

Authoritative Canadian hydrographic data is available under the Open Government Licence \- Canada from several sources:

* **Open Government Portal:** The primary access point for both the new CHN and the legacy NHN datasets, available in formats like GeoPackage and File Geodatabase.20  
* **Provincial Data Catalogues:** For the significant portion of Cascadia that lies within British Columbia, the **BC Freshwater Atlas** is an exceptionally high-quality and standardized data source that should be prioritized.34 It provides detailed watershed boundaries and a connected stream network for the entire province.

**Table 3.1: Comparison of U.S. and Canadian Watershed Classification Systems**

| Feature | U.S. System (WBD/HUC) | Canadian System (SDAC/CHN) |
| :---- | :---- | :---- |
| **Primary Agency** | U.S. Geological Survey (USGS) | Natural Resources Canada (NRCan), Statistics Canada |
| **Core Dataset** | Watershed Boundary Dataset (WBD) | Canadian Hydrospatial Network (CHN), National Hydro Network (NHN) |
| **Hierarchical Code** | Hydrologic Unit Code (HUC) | Standard Drainage Area Code (SDAC), CHN Identifiers |
| **Granularity Levels** | HUC2, HUC4, HUC6, HUC8, HUC10, HUC12 (complete) | MDA, SDA, SSDA (SDAC); Work Unit, Catchment (CHN) |
| **Coding Scheme** | Numeric (e.g., 170101010101\) | Alphanumeric (e.g., 08GA) |
| **Data Model** | Polygon dataset with HUC attributes. | Network model with flowlines, catchments, waterbodies, etc. |
| **Acquisition Source** | USGS National Map, NRCS Data Gateway | Open Government Portal, Provincial Catalogues (e.g., BC) |

---

### **Part II: Data Processing and Harmonization — Creating a Unified Cascadia Watershed Layer**

This part details the technical workflow for the pre-computation (offline) strategy. It provides a step-by-step guide for the Extract, Transform, and Load (ETL) process required to build the single, queryable data layer that will power the final application. This unified layer is the core asset of the recommended architecture.

#### **Section 4: The Core Workflow: High-Level Architecture**

The application's logic will follow two main stages: converting user input into a location, and then using that location to query the pre-built watershed data.

##### **4.1 Geocoding User Input**

The first step in any user request is to translate a human-readable address (e.g., "123 Main St, Seattle, WA") or postal/zip code into machine-readable geographic coordinates (latitude and longitude). This process, known as geocoding, is accomplished by calling an external Application Programming Interface (API). Several commercial and free services are available.

A critical consideration when selecting a geocoding provider is its terms of service, particularly regarding the storage of results. Some services, especially those with generous free tiers, may prohibit the permanent caching or storage of the coordinates they return. For an application that might experience repeated queries for the same locations, the ability to cache results can significantly improve performance and reduce costs. Services like Mapbox explicitly offer a "Permanent Geocoding" option, which, while potentially more expensive, provides the necessary licensing rights for such an architecture.36 This choice has direct implications for both the application's design and its operational budget.

**Table 4.1: Geocoding API Comparison**

| API Provider | Free Tier Limit | Cost Structure | Key Features | Link to Docs |
| :---- | :---- | :---- | :---- | :---- |
| **geocode.maps.co** | 1 req/sec; 5,000/day | Paid plans for higher volume | Simple, generous free tier | 37 |
| **Mapbox Geocoding** | Generous free monthly requests | Pay-as-you-go after free tier | Permanent storage option, batch processing, advanced features | 36 |
| **Positionstack** | 100 requests/month | Paid plans start at \~$10/month | Batch requests, worldwide coverage | 38 |
| **OpenWeather Geocoding** | Included with API key | Part of weather API subscription | Direct and reverse geocoding, supports zip/post code | 39 |

##### **4.2 The Point-in-Polygon Test**

Once a latitude-longitude coordinate pair is obtained, the central geospatial operation is to determine which watershed polygon from the prepared dataset contains that point. This is a fundamental GIS task known as a point-in-polygon (PIP) query.40 This operation takes the input point and the collection of watershed polygons and returns the specific polygon that spatially encloses the point. Modern geospatial libraries are highly optimized to perform this query efficiently.

#### **Section 5: Data Preparation: Forging the Unified Dataset**

This section provides a detailed, step-by-step guide for the most critical and complex part of the offline approach: creating the single, harmonized geospatial file that will serve as the application's local database.

##### **5.1 Step 1: Data Extraction and Clipping**

The initial step is to reduce the vast national datasets to only the data relevant to the project.

1. **Download Source Data:** Acquire the full U.S. WBD (specifically the HUC12 polygon layer) and the most comprehensive Canadian data available (a composite of CHN catchments, NHN SSDAs, and/or BC Freshwater Atlas watersheds).  
2. **Load AOI:** Load the authoritative Cascadia Bioregion AOI polygon defined in Section 1\.  
3. **Clip Datasets:** Using a standard GIS tool or library (like GeoPandas or QGIS), perform a spatial "clip" operation. This will trim the U.S. and Canadian watershed layers to the exact extent of the Cascadia AOI polygon. This is a crucial optimization that dramatically reduces the file size and the amount of data the application needs to process, focusing it solely on the bioregion.

##### **5.2 Step 2: Reprojection to a Common CRS**

Geospatial data from different national sources will invariably be in different Coordinate Reference Systems (CRS). For example, U.S. data is often in a variant of the North American Datum 1983 (NAD83), while Canadian data may use another.12 For any spatial comparison or operation to be valid, all data layers must exist within the same CRS.

1. **Identify Source CRS:** Inspect the metadata of the U.S. data, the Canadian data, and the Cascadia AOI file to determine their native CRS.  
2. **Select Target CRS:** Choose a single, appropriate CRS for the entire project. Since the AOI file from WWU was delineated in a Lambert Azimuthal Equal Area system, using that same projection or a similar equal-area projection suitable for the Pacific Northwest (e.g., EPSG:3310, NAD83 / California Albers) is recommended. Equal-area projections are ideal as they preserve the area measurements of the polygons.  
3. **Reproject All Layers:** Transform the U.S. watershed layer, the Canadian watershed layer, and the AOI layer into the selected target CRS. This step is an absolute prerequisite for accurate spatial analysis. As documented in GIS user forums, mismatched CRS is a frequent cause of failed or incorrect point-in-polygon and other spatial join operations.41

##### **5.3 Step 3: Schema Harmonization and Merging**

This is the most intellectually demanding step of the process. The U.S. WBD and the various Canadian datasets have entirely different attribute table structures (schemas). They cannot be simply appended together. A new, unified schema must be designed to accommodate information from both sources gracefully.

A script must be developed to perform this transformation. It will read the clipped U.S. data, map its relevant fields (like huc12, name, states) to the new unified schema, and then do the same for the clipped Canadian data (mapping fields like wscssda, wscsdaname). The two transformed datasets can then be merged into a single file. For U.S.-sourced polygons, the Canadian-specific fields will be null, and vice-versa. This approach creates a single, consistent data structure for the entire bioregion.

**Table 5.1: Proposed Unified Cascadia Watershed Data Schema**

| Field Name | Data Type | Description | U.S. Source Field (WBD) | Canadian Source Field (CHN/SDAC) |
| :---- | :---- | :---- | :---- | :---- |
| geometry | Polygon | The polygon geometry of the watershed unit. | geometry | geometry |
| unique\_id | String | A unique identifier for the polygon. | huc12 | catchment\_id or wscssda |
| watershed\_name | String | The common name of the watershed unit. | name | geoname or wscssdaname\_en |
| country | String | The country of origin ('USA' or 'CAN'). | (Derived) | (Derived) |
| source\_dataset | String | The original dataset (e.g., 'USGS WBD', 'NRCan CHN'). | (Derived) | (Derived) |
| huc12\_code | String | The 12-digit Hydrologic Unit Code. | huc12 | NULL |
| huc10\_code | String | The 10-digit Hydrologic Unit Code. | (Derived from huc12) | NULL |
| huc8\_code | String | The 8-digit Hydrologic Unit Code. | (Derived from huc12) | NULL |
| sdac\_ssda\_code | String | The Sub-Sub-Drainage Area code. | NULL | wscssda |
| sdac\_sda\_code | String | The Sub-Drainage Area code. | NULL | (Derived from wscssda) |
| sdac\_mda\_code | String | The Major Drainage Area code. | NULL | (Derived from wscssda) |
| area\_sqkm | Float | The area of the polygon in square kilometers. | areasqkm | area\_sqkm |

##### **5.4 Step 4: Spatial Indexing**

The final merged dataset, while clipped, will still contain many thousands of polygons. To ensure that point-in-polygon queries are fast, the data file must have a spatial index. This is a special data structure, typically an R-tree, that allows the query algorithm to quickly discard the vast majority of polygons that are nowhere near the input point, dramatically speeding up the search. Most modern geospatial file formats (like GeoPackage) and libraries (like GeoPandas) create and use these indexes automatically, but its importance for achieving acceptable application performance cannot be overstated.41

---

### **Part III: Implementation Blueprints**

This part translates the prepared data and conceptual workflow into two potential software architectures. It provides a detailed analysis of each, including code-level guidance for the recommended approach, to give the developer a clear path to implementation.

#### **Section 6: Blueprint A: The Recommended Offline/Local Implementation**

This architecture represents the most robust, reliable, and performant solution. It is based on performing the complex data harmonization work once, offline, and then bundling the resulting unified data file with the application. This approach provides complete, guaranteed coverage of the Cascadia bioregion and removes dependencies on external services for the core watershed query.

##### **6.1 System Architecture**

The system is designed around a local, pre-processed data file.

1. **Data Asset:** The application includes the unified Cascadia watershed file (e.g., cascadia\_watersheds.gpkg) created in Part II.  
2. **User Input:** The user provides an address or postal code.  
3. **Geocoding:** The application sends the input to an external geocoding API (as analyzed in Section 4.1) to get a latitude-longitude coordinate.  
4. Local Query:  
   a. The application loads the local cascadia\_watersheds.gpkg file into a geopandas GeoDataFrame.  
   b. It creates a second, single-row GeoDataFrame containing the point geometry from the geocoded coordinates.  
   c. It performs a spatial join (geopandas.sjoin) between the point and the watershed polygons.  
5. **Result Processing:** The result of the join is a new GeoDataFrame containing the single row from the watershed layer that contains the point. The application extracts the attributes (names, codes, etc.) from this row.  
6. **Output:** The application formats the extracted information and returns it to the user.

##### **6.2 Python Implementation with GeoPandas**

The following Python code snippets illustrate the core logic using the geopandas library. This approach leverages highly optimized, pre-compiled code for geospatial operations.

Code Snippet 1: Loading Data and Performing the Spatial Join  
This demonstrates the central query operation. It assumes the cascadia\_watersheds.gpkg file has been created and is accessible.

Python

import geopandas as gpd  
from shapely.geometry import Point

\# \--- Pre-computation: Load watershed data once \---  
\# This should be done once when the application starts to avoid reloading the file on every request.  
try:  
    watersheds\_gdf \= gpd.read\_file("cascadia\_watersheds.gpkg")  
except Exception as e:  
    print(f"Error loading watershed file: {e}")  
    \# Handle error appropriately  
      
\# \--- Per-request function \---  
def find\_watershed(lat, lon, watersheds\_data):  
    """  
    Finds the watershed containing the given latitude and longitude.

    Args:  
        lat (float): Latitude of the point.  
        lon (float): Longitude of the point.  
        watersheds\_data (GeoDataFrame): Pre-loaded GeoDataFrame of Cascadia watersheds.

    Returns:  
        GeoDataFrame: A GeoDataFrame containing the matching watershed's data, or an empty one if no match.  
    """  
    \# 1\. Create a GeoDataFrame for the input point  
    point\_geom \= Point(lon, lat)  
    \# Ensure the point uses the same CRS as the watershed data  
    point\_gdf \= gpd.GeoDataFrame(, geometry=\[point\_geom\], crs=watersheds\_data.crs)

    \# 2\. Perform the spatial join (point-in-polygon)  
    \# This is highly optimized and uses the spatial index.  
    \# op='within' finds polygons that contain the point.  
    \# how='inner' ensures only the matching polygon is returned.  
    try:  
        \# The sjoin operation is the performant way to do this \[41\]  
        result\_gdf \= gpd.sjoin(point\_gdf, watersheds\_data, how="inner", op="within")  
        return result\_gdf  
    except Exception as e:  
        print(f"Error during spatial join: {e}")  
        return gpd.GeoDataFrame()

\# \--- Example Usage \---  
\# Assume geocoding returned these coordinates for a location in Seattle  
seattle\_lat, seattle\_lon \= 47.6062, \-122.3321

\# Call the function with the pre-loaded data  
watershed\_info \= find\_watershed(seattle\_lat, seattle\_lon, watersheds\_gdf)

if not watershed\_info.empty:  
    print("Watershed found:")  
    \# Print the first row of the result as a dictionary  
    print(watershed\_info.iloc.to\_dict())  
else:  
    print("No watershed found for the given coordinates within the Cascadia bioregion.")

##### **6.3 Performance Considerations**

The primary performance bottleneck in a naive implementation would be iterating through every polygon and performing an individual .within() check.42 This would be unacceptably slow for a dataset of this size. The

geopandas.sjoin method, however, is the correct and highly performant solution. It utilizes the underlying spatial index of the dataset to rapidly narrow down the search space, making the query time logarithmic rather than linear with respect to the number of polygons.41

The main trade-off is the initial memory footprint and load time of the cascadia\_watersheds.gpkg file. For a web service, this file should be loaded into memory once when the service starts, not on every incoming request. This amortizes the loading cost across all subsequent queries, resulting in very fast response times for individual lookups.

#### **Section 7: Blueprint B: The API-Driven (Online) Implementation**

This section explores a purely API-driven alternative, analyzing its feasibility, benefits, and significant drawbacks. This approach would avoid the need for local data storage and pre-processing but introduces dependencies and coverage issues.

##### **7.1 U.S. Watershed Lookup via API**

For the U.S. portion, several APIs could potentially provide the needed information.

* **USGS Water Services:** The legacy Site Service allows for queries by a bounding box (bBox).43 A developer could query for the nearest monitoring site to a given coordinate and then request the  
  expanded site output, which includes the HUC for that site.43 This is an indirect method that relies on the proximity of a monitoring station, which may not always be accurate for determining the watershed of the query point itself.  
* **EPA Hydrologic Microservices (HMS) and StreamCat API:** This is a more promising avenue. The EPA's StreamCat dataset provides a wealth of watershed metrics but is indexed by a stream segment identifier called a COMID.45 The key is converting a latitude/longitude point to a  
  COMID. Documentation for various EPA HMS APIs (for precipitation, humidity, etc.) reveals a common input structure that accepts either a COMID or a Latitude and Longitude pair.47 Furthermore, the  
  watershed workflow endpoint explicitly includes a point object with latitude and longitude in its request body schema.50 This strongly indicates the existence of an internal EPA service that performs a point-in-polygon lookup against the NHDPlusV2 catchment layer to find the corresponding  
  COMID. If this lat/lon-to-COMID service endpoint can be accessed directly, it would be the most efficient API-based method for the U.S.

##### **7.2 Canadian Watershed Lookup via API**

The primary weakness of the online approach is the lack of a comparable service for Canada. Research into NRCan and other Canadian data portals does not reveal a simple, public-facing API that takes a latitude/longitude coordinate and returns a corresponding SDAC or CHN catchment identifier.52 While datasets are available as Web Map Services (WMS) for visualization or as ESRI Feature Services 54, using them for this purpose would require implementing a more complex spatial query against the service endpoint (

query operation with geometry). This is less reliable, may have performance limitations, and is not a simple lookup. The BC Freshwater Atlas provides extensive data but its primary access is through downloads or the iMapBC viewer, not a simple lookup API.35

##### **7.3 Architectural Trade-offs and Recommendation**

The choice between these two architectures involves significant trade-offs in reliability, performance, and completeness.

**Table 7.1: Comparison of Offline vs. Online Architectures**

| Criteria | Blueprint A: Offline/Local | Blueprint B: Online/API |
| :---- | :---- | :---- |
| **Coverage** | **Excellent.** Guarantees 100% coverage of the defined Cascadia AOI. | **Poor.** Incomplete. No clear, comprehensive API for the Canadian portion. |
| **Reliability** | **High.** No dependency on external API uptime for core function. | **Low.** Dependent on multiple external APIs (Geocoding, USGS/EPA, Canadian services). An outage in any one service breaks the function. |
| **Performance** | **High.** Very fast queries after initial data load. | **Variable.** Dependent on network latency and external API response times. |
| **Data Granularity** | **Excellent.** Full control over the data allows for any level of granularity. | **Limited.** Restricted to the granularity provided by the API endpoints. |
| **Maintenance Effort** | **Periodic.** Requires a scheduled process to download and re-process new data versions. | **Low.** No local data to maintain. Relies on providers to keep data current. |
| **Implementation Complexity** | **High upfront.** Requires significant data processing and harmonization work. | **High ongoing.** Requires managing multiple different API clients and fallback logic for service failures or gaps in coverage. |

**Final Recommendation:** **Blueprint A (Offline/Local Implementation) is strongly recommended.**

The primary requirement of the project is to provide a function that works for *all of Cascadia*. The online/API-driven approach fails this fundamental test due to the lack of a comprehensive API for the Canadian portion of the bioregion. The offline approach, while requiring a significant upfront investment in data processing, is the only method that can deliver a robust, reliable, and complete solution. The one-time cost of creating the unified data file yields a far superior system that the developer can control and depend on.

---

### **Part IV: Delivering Results and Long-Term System Maintenance**

This final part addresses the user's specific output requirements and outlines a strategy for ensuring the application's underlying data remains current over time.

#### **Section 8: Structuring the Output: From Polygon to Watershed Lineage**

The user requires not just the name of the immediate watershed but also information on its parent watersheds, providing a full "lineage." The unified data schema proposed in Table 5.1 is explicitly designed to facilitate this.

##### **8.1 Providing Hierarchical Data**

Once the sjoin operation identifies the containing polygon, the application has access to its entire attribute row. This row contains the finest-granularity codes (huc12\_code for the U.S., sdac\_ssda\_code for Canada). The hierarchical nature of these coding systems allows for simple string manipulation to derive the parent codes.

* **For a U.S. Point:** If the result contains a huc12\_code of 170101010101, the application can programmatically derive:  
  * huc10\_code: 1701010101 (the first 10 digits)  
  * huc8\_code: 17010101 (the first 8 digits)  
  * And so on for HUC6, HUC4, and HUC2.  
    The application can then use these derived codes to look up the corresponding names from the unified data table or from a separate lookup table.  
* **For a Canadian Point:** A similar logic applies to the sdac\_ssda\_code. If the code is 08GA, the application knows:  
  * sdac\_sda\_code: 08G (the first three characters)  
  * sdac\_mda\_code: 08 (the first two characters)

A function can be written to take the full record from the spatial join and return a structured JSON object containing this complete lineage, which can then be displayed to the user.

##### **8.2 Delivering Boundary Data**

The user also requested "mappings to boundaries." The geometry column of the GeoDataFrame returned by the sjoin operation contains the precise polygon boundary of the identified watershed. This geometry object can be easily serialized into a standard web-friendly format like GeoJSON or Well-Known Text (WKT). This serialized geometry can then be passed to a front-end mapping library (such as Leaflet, Mapbox GL JS, or OpenLayers) to be drawn on an interactive map, visually showing the user the extent of their watershed.

#### **Section 9: A Strategy for Long-Term Data Currency**

A key consideration for any data-driven application is ensuring the data does not become stale. The authoritative national datasets are updated periodically as new information becomes available or delineations are improved.11

##### **9.1 Monitoring for Updates**

The developer should establish a process to monitor the primary data sources for new releases. This involves periodically checking the USGS National Map and the NRCan Open Government Portal for announcements about new versions of the WBD and CHN, respectively.

##### **9.2 The Refresh Process**

A semi-automated data refresh process, executed on a scheduled basis (e.g., annually or biennially), is the recommended strategy. The process would be:

1. **Check for New Versions:** A script or manual check determines if a newer version of the WBD or CHN has been released since the last update.  
2. **Execute the Pipeline:** If new data is available, the entire data processing and harmonization pipeline described in Part II is re-run. This includes downloading the new source files, clipping, re-projecting, harmonizing the schema, and merging them.  
3. **Deploy New Asset:** The newly generated cascadia\_watersheds.gpkg file is then bundled into a new release of the application, replacing the older version.

This strategy balances the need for data currency with the stability and reliability of the offline architecture. It avoids the complexities and potential fragility of trying to fetch real-time data updates while ensuring that the application's foundational data accurately reflects the best available science over the long term.

#### **Works cited**

1. Cascadia (bioregion) \- Wikipedia, accessed June 18, 2025, [https://en.wikipedia.org/wiki/Cascadia\_(bioregion)](https://en.wikipedia.org/wiki/Cascadia_\(bioregion\))  
2. Bioregional Boundaries \- Cascadia Department of Bioregion, accessed June 18, 2025, [https://cascadiabioregion.org/bioregional-boundaries](https://cascadiabioregion.org/bioregional-boundaries)  
3. Nine Regions of Cascadia, accessed June 18, 2025, [https://cascadiabioregion.org/nine-regions-of-cascadia](https://cascadiabioregion.org/nine-regions-of-cascadia)  
4. Cascadia Map \- Sightline Institute, accessed June 18, 2025, [https://www.sightline.org/cascadia-map/](https://www.sightline.org/cascadia-map/)  
5. Mapping Cascadia — CascadiaNow\!, accessed June 18, 2025, [https://www.cascadianow.org/mapping-cascadia](https://www.cascadianow.org/mapping-cascadia)  
6. Cascadia Bioregion Boundary \- Overview, accessed June 18, 2025, [https://www.arcgis.com/home/item.html?id=c6497941559d433da98e286fb3f63551](https://www.arcgis.com/home/item.html?id=c6497941559d433da98e286fb3f63551)  
7. Cascadia Bioregion Atlas \- WordPress for WWU, accessed June 18, 2025, [https://wp.wwu.edu/cascadia/](https://wp.wwu.edu/cascadia/)  
8. Cascadia Bioregion \- Sightline (PDF), accessed June 18, 2025, [https://www.cascadianow.org/media/cascadia-bioregion-sightline-pdf](https://www.cascadianow.org/media/cascadia-bioregion-sightline-pdf)  
9. River Basin Map of the Cascadia Bioregion of North America, accessed June 18, 2025, [https://cascadiabioregion.org/department-of-bioregion/watershed-map-of-the-cascadia-bioregion-of-north-america](https://cascadiabioregion.org/department-of-bioregion/watershed-map-of-the-cascadia-bioregion-of-north-america)  
10. Cascadia Subduction Zone Database | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/special-topics/subduction-zone-science/science/cascadia-subduction-zone-database](https://www.usgs.gov/special-topics/subduction-zone-science/science/cascadia-subduction-zone-database)  
11. Watershed Boundary Dataset (WBD) \- USGS National Map Downloadable Data Collection, accessed June 18, 2025, [https://data.usgs.gov/datacatalog/data/USGS:0101bc32-916e-481d-8654-db7f8509fd0c](https://data.usgs.gov/datacatalog/data/USGS:0101bc32-916e-481d-8654-db7f8509fd0c)  
12. Watershed Boundary Dataset (WBD) \- NRCS Geospatial Data Gateway, accessed June 18, 2025, [https://datagateway.nrcs.usda.gov/catalog/productdescription/wbd.html](https://datagateway.nrcs.usda.gov/catalog/productdescription/wbd.html)  
13. Watershed Boundary Dataset (WBD) Data Dictionary | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/ngp-standards-and-specifications/watershed-boundary-dataset-wbd-data-dictionary](https://www.usgs.gov/ngp-standards-and-specifications/watershed-boundary-dataset-wbd-data-dictionary)  
14. 9c. What U.S. Geological Survey Hydrological Unit Code (HUC) is the project in? \- ORIA, accessed June 18, 2025, [https://www.oria.wa.gov/DesktopModules/GuidanceHelp/View.aspx?node=759](https://www.oria.wa.gov/DesktopModules/GuidanceHelp/View.aspx?node=759)  
15. Hydrologic Units of the United States \- Water Resources Mission Area \- USGS.gov, accessed June 18, 2025, [https://water.usgs.gov/themes/hydrologic-units/](https://water.usgs.gov/themes/hydrologic-units/)  
16. Codex \- Hydrologic Unit Code | ADBNet \- Iowa DNR, accessed June 18, 2025, [https://programs.iowadnr.gov/adbnet/Docs/Codex/Hydrologic%20Unit%20Code](https://programs.iowadnr.gov/adbnet/Docs/Codex/Hydrologic%20Unit%20Code)  
17. Hydrologic unit codes \- USGS Water Data for the Nation Help, accessed June 18, 2025, [https://help.waterdata.usgs.gov/code/hucs\_query?fmt=html](https://help.waterdata.usgs.gov/code/hucs_query?fmt=html)  
18. National Hydrography | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/programs/national-geospatial-program/national-hydrography](https://www.usgs.gov/programs/national-geospatial-program/national-hydrography)  
19. Watershed Boundary Dataset | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/watershed-boundary-dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset)  
20. National Hydro Network \- NHN \- GeoBase Series \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/a4b190fe-e090-4e6d-881e-b87956c07977](https://open.canada.ca/data/en/dataset/a4b190fe-e090-4e6d-881e-b87956c07977)  
21. National Hydro Network (NHN) \- Leddy Library, accessed June 18, 2025, [https://leddy.uwindsor.ca/national-hydro-network-nhn](https://leddy.uwindsor.ca/national-hydro-network-nhn)  
22. Canadian Hydrospatial Network \- Natural Resources Canada, accessed June 18, 2025, [https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-portals-tools-services/canadian-hydrospatial-network](https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-portals-tools-services/canadian-hydrospatial-network)  
23. Canadian Hydrospatial Network (CHN) Data Model Edition 0.2 2025 ..., accessed June 18, 2025, [ftp://ftp.geogratis.gc.ca/pub/nrcan\_rncan/vector/chn\_rhc/doc/CHN\_GeoBase\_Series\_Data\_Models\_EN\_V\_0\_2.pdf](ftp://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/chn_rhc/doc/CHN_GeoBase_Series_Data_Models_EN_V_0_2.pdf)  
24. The New Canadian Hydrospatial Network (CHN) – Advancements in Hydrography for Improved Modelling | Schedule | GeoIgnite 2025 \- Browser not Supported, accessed June 18, 2025, [https://sites.grenadine.co/sites/gogeomatics/en/geoignite-2025/schedule/21437/The%20New%20Canadian%20Hydrospatial%20Network%20%28CHN%29%20%E2%80%93%20Advancements%20in%20Hydrography%20for%20Improved%20Modelling?signups=0\&tags=47\&updated=0\&view\_setting=calendar](https://sites.grenadine.co/sites/gogeomatics/en/geoignite-2025/schedule/21437/The%20New%20Canadian%20Hydrospatial%20Network%20%28CHN%29%20%E2%80%93%20Advancements%20in%20Hydrography%20for%20Improved%20Modelling?signups=0&tags=47&updated=0&view_setting=calendar)  
25. Hydrographic Networks \- Natural Resources Canada, accessed June 18, 2025, [https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-tools-services/hydrographic-networks](https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-tools-services/hydrographic-networks)  
26. Standard Drainage Area Classification (SDAC) 2003, accessed June 18, 2025, [https://www.statcan.gc.ca/en/subjects/standard/sdac/sdacinfo1](https://www.statcan.gc.ca/en/subjects/standard/sdac/sdacinfo1)  
27. Standard Drainage Area Classification (SDAC) 2003 \- Statistique Canada, accessed June 18, 2025, [https://www23.statcan.gc.ca/imdb/p3VD.pl?Function=getVD\&TVD=134769](https://www23.statcan.gc.ca/imdb/p3VD.pl?Function=getVD&TVD=134769)  
28. Watersheds in Canada \- Overview, accessed June 18, 2025, [https://www.arcgis.com/home/item.html?id=12b6e33d5a754c92b97ae5d0fed6940a](https://www.arcgis.com/home/item.html?id=12b6e33d5a754c92b97ae5d0fed6940a)  
29. Atlas of Canada \- Major Drainage Areas of Canada \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/74eb52a9-c088-401c-bfb3-f08a18899e7b](https://open.canada.ca/data/en/dataset/74eb52a9-c088-401c-bfb3-f08a18899e7b)  
30. Sub-sub-basins of the AAFC Watersheds Project \- 2013 \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/0e62c919-4933-40d4-8e77-8057f343e8af](https://open.canada.ca/data/en/dataset/0e62c919-4933-40d4-8e77-8057f343e8af)  
31. Major drainage areas and sub-drainage areas, accessed June 18, 2025, [https://www.statcan.gc.ca/en/subjects/standard/sdac/maps/m004](https://www.statcan.gc.ca/en/subjects/standard/sdac/maps/m004)  
32. Canadian Hydrospatial Network \- CHN \- GEO.CA Viewer, accessed June 18, 2025, [https://app.geo.ca/result/en/canadian-hydrospatial-network---chn?id=ae385105-e48c-4b54-bd0f-dfb7303301cb\&lang=en](https://app.geo.ca/result/en/canadian-hydrospatial-network---chn?id=ae385105-e48c-4b54-bd0f-dfb7303301cb&lang=en)  
33. Canadian Hydrospatial Network \- CHN \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb](https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb)  
34. Freshwater Atlas Watersheds \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/3ee497c4-57d7-47f8-b030-2e0c03f8462a](https://open.canada.ca/data/en/dataset/3ee497c4-57d7-47f8-b030-2e0c03f8462a)  
35. Freshwater Atlas \- Province of British Columbia \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/freshwater](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/freshwater)  
36. Geocoding \- Free Address and Places Search \- Mapbox, accessed June 18, 2025, [https://www.mapbox.com/geocoding](https://www.mapbox.com/geocoding)  
37. Free Geocoding API \- Geocode Addresses & Coordinates, accessed June 18, 2025, [https://geocode.maps.co/](https://geocode.maps.co/)  
38. Global Geocoding API \- Positionstack, accessed June 18, 2025, [https://positionstack.com/](https://positionstack.com/)  
39. Geocoding API \- OpenWeatherMap, accessed June 18, 2025, [https://openweathermap.org/api/geocoding-api](https://openweathermap.org/api/geocoding-api)  
40. Point-in-polygon queries \- Automating GIS Processes, accessed June 18, 2025, [https://autogis-site.readthedocs.io/en/latest/lessons/lesson-3/point-in-polygon-queries.html](https://autogis-site.readthedocs.io/en/latest/lessons/lesson-3/point-in-polygon-queries.html)  
41. Accelerating GeoPandas for selecting points inside polygon \- GIS StackExchange, accessed June 18, 2025, [https://gis.stackexchange.com/questions/346550/accelerating-geopandas-for-selecting-points-inside-polygon](https://gis.stackexchange.com/questions/346550/accelerating-geopandas-for-selecting-points-inside-polygon)  
42. geopandas.GeoSeries.contains, accessed June 18, 2025, [https://geopandas.org/docs/reference/api/geopandas.GeoSeries.contains.html](https://geopandas.org/docs/reference/api/geopandas.GeoSeries.contains.html)  
43. Site Service Details | Water Services Web, accessed June 18, 2025, [https://waterservices.usgs.gov/docs/site-service/site-service-details/](https://waterservices.usgs.gov/docs/site-service/site-service-details/)  
44. Water Services Test Tool, accessed June 18, 2025, [https://waterservices.usgs.gov/test-tools/?service=iv](https://waterservices.usgs.gov/test-tools/?service=iv)  
45. StreamCat Dataset | US EPA, accessed June 18, 2025, [https://www.epa.gov/national-aquatic-resource-surveys/streamcat-dataset](https://www.epa.gov/national-aquatic-resource-surveys/streamcat-dataset)  
46. StreamCat Dataset \- ReadMe | US EPA, accessed June 18, 2025, [https://www.epa.gov/national-aquatic-resource-surveys/streamcat-dataset-readme](https://www.epa.gov/national-aquatic-resource-surveys/streamcat-dataset-readme)  
47. Evapotranspiration \- HMS: Hydrologic Micro Services | United States Environmental Protection Agency | US EPA, accessed June 18, 2025, [https://qed.epa.gov/hms/hydrology/evapotranspiration/](https://qed.epa.gov/hms/hydrology/evapotranspiration/)  
48. Meteorology \- Humidity \- HMS: Hydrologic Micro Services | United States Environmental Protection Agency | US EPA, accessed June 18, 2025, [https://qed.epa.gov/hms/meteorology/humidity/](https://qed.epa.gov/hms/meteorology/humidity/)  
49. Meteorology \- Precipitation \- HMS: Hydrologic Micro Services | United States Environmental Protection Agency | US EPA, accessed June 18, 2025, [https://qed.epa.gov/hms/meteorology/precipitation/](https://qed.epa.gov/hms/meteorology/precipitation/)  
50. POST method for submitting a request for getting workflow compare data. Source parameter must contain a value, but value is not used. | Hydrologic Micro Services (HMS) REST API \- Postman, accessed June 18, 2025, [https://www.postman.com/api-evangelist/environmental-protection-agency-epa/request/egidfx0/post-method-for-submitting-a-request-for-getting-workflow-compare-data-source-parameter-must-contain-a-value-but-value-is-not-used](https://www.postman.com/api-evangelist/environmental-protection-agency-epa/request/egidfx0/post-method-for-submitting-a-request-for-getting-workflow-compare-data-source-parameter-must-contain-a-value-but-value-is-not-used)  
51. POST method for submitting a request for total flow data. | Hydrologic Micro Services (HMS) REST API \- Postman, accessed June 18, 2025, [https://www.postman.com/api-evangelist/environmental-protection-agency-epa/request/zi0jqcd/post-method-for-submitting-a-request-for-total-flow-data](https://www.postman.com/api-evangelist/environmental-protection-agency-epa/request/zi0jqcd/post-method-for-submitting-a-request-for-total-flow-data)  
52. Web Services \- Natural Resources Canada, accessed June 18, 2025, [https://natural-resources.canada.ca/science-data/science-research/geomatics/web-services](https://natural-resources.canada.ca/science-data/science-research/geomatics/web-services)  
53. Natural Resources Canada \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/organization/nrcan-rncan?\_keywords\_limit=0\&keywords=Water&\_subject\_limit=0\&subject=nature\_and\_environment](https://open.canada.ca/data/organization/nrcan-rncan?_keywords_limit=0&keywords=Water&_subject_limit=0&subject=nature_and_environment)  
54. Watersheds in Canada \- ArcGIS Hub, accessed June 18, 2025, [https://hub.arcgis.com/maps/12b6e33d5a754c92b97ae5d0fed6940a](https://hub.arcgis.com/maps/12b6e33d5a754c92b97ae5d0fed6940a)  
55. iMapBC \- Province of British Columbia \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/gov/content/data/geographic-data-services/web-based-mapping/imapbc](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/web-based-mapping/imapbc)