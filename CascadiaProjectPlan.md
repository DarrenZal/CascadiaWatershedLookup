

# **Technical Assessment and Integration Strategy for Canadian Hydrographic Data in the Cascadia Bioregion**

## **Executive Summary**

This report provides a comprehensive technical assessment of available Canadian hydrographic data for British Columbia (BC) and presents a detailed strategy for its integration with the United States Watershed Boundary Dataset (WBD) to create a seamless, cross-border watershed identification service for the Cascadia bioregion. The analysis concludes that the development of such a service is highly feasible using currently available, high-quality, open-licensed data.

The primary federal dataset for Canada, the new Canadian Hydrospatial Network (CHN), represents the ideal future standard for this project. It is an analysis-ready, high-resolution network explicitly designed for harmonization with its US counterpart, the 3D Hydrography Program (3DHP). However, the CHN rollout is in its nascent stages and currently has no data coverage for British Columbia, rendering it unsuitable for immediate implementation.

Therefore, this report recommends a robust, hybrid data architecture that leverages the most authoritative dataset for each geographic domain:

1. **United States Domain:** The standard USGS Watershed Boundary Dataset (WBD).  
2. **Transboundary Domain:** The pre-harmonized watershed polygons developed by the International Joint Commission (IJC), which are now distributed as an integral part of the standard USGS WBD for border regions.  
3. **Canadian Interior Domain:** The British Columbia Freshwater Atlas (FWA), specifically the **FWA Assessment Watersheds** dataset, which is the authoritative provincial standard.

This hybrid approach capitalizes on the extensive harmonization work already completed by the IJC, which has solved the most complex challenge of reconciling geometries and attributes directly at the international boundary. The integration task is thus simplified to a spatial stitching of the BC FWA data to the inland edge of this authoritative transboundary block.

This document provides a detailed, step-by-step technical workflow for this integration, including data preparation, spatial joining, and the creation of a unified identification system and topological network. A proposed schema for the final, unified database is presented to serve as a blueprint for development. Finally, a long-term strategy is outlined for migrating the Canadian data component to the CHN once coverage for British Columbia becomes available, ensuring the project is built on a foundation that is both immediately viable and future-proof.

## **The Evolving Federal Standard: Canadian Hydrospatial Network (CHN)**

The Canadian Hydrospatial Network (CHN) is the Government of Canada's next-generation hydrographic data product. It represents a fundamental modernization of Canada's approach to water data, moving from a static, cartographic product to a dynamic, analysis-ready network designed for sophisticated modeling and water resource management. Understanding its mandate, status, and long-term trajectory is critical for planning any new hydrographic data-dependent project.

### **Mandate and Strategic Alignment**

The CHN is the designated successor to the legacy National Hydrographic Network (NHN) and is being developed by the Canada Centre for Mapping and Earth Observation (CCMEO), a division of Natural Resources Canada (NRCan).1 Its core mandate is to provide a geospatial network of features that enables the advanced modeling of surface water flow across Canada.4 This purpose-built design for analysis supports a wide range of applications, including hydrologic and hydraulic modeling, flood hazard mapping, nutrient transport tracking, and climate impact studies.5

A paramount feature of the CHN's design is its strategic alignment with hydrographic modernization efforts in the United States. The CHN physical model and its features are being developed to be "closely aligned and harmonized with the USGS 3DHP hydrographic network".4 The 3D Hydrography Program (3DHP) is the successor to the NHD and WBD in the United States.9 This deliberate, built-in compatibility is the single most important long-term consideration for a cross-border project. It signals a future where transboundary hydrographic analysis is a native capability of the official national datasets, rather than a complex, ad-hoc integration challenge. Any system architected today must therefore anticipate and plan for an eventual migration to this harmonized CHN/3DHP ecosystem to ensure long-term viability and efficiency.

### **Current Status and Coverage in British Columbia**

The rollout of the CHN is an ongoing process, with data being produced and disseminated in "work units." A work unit is a hydrologically connected geographic area, such as a single large watershed or a group of smaller adjacent watersheds, which provides a more natural and analytically coherent method for data delivery compared to arbitrary map tiles.4

However, the CHN program is still in its early stages. As of late 2024, released work units and active production areas are concentrated in Eastern Canada. The initial public dataset covered the Miramichi watershed in New Brunswick, and subsequent efforts have focused on New Brunswick, the Gaspésie region of Quebec, Nova Scotia, and Prince Edward Island.5

**There is currently no evidence of any completed or released CHN work units for British Columbia**.5 The national rollout is intrinsically linked to the availability of high-resolution source data, particularly LiDAR-derived High Resolution Digital Elevation Models (HRDEM) and high-resolution optical imagery, which are foundational inputs for the automated feature extraction process.3 The production schedule for CHN in BC is therefore dependent on the progress of NRCan's National Elevation Data Strategy in acquiring HRDEM coverage for the province. This dependency provides a tangible metric for long-term project planning; monitoring the public progress of HRDEM acquisition in BC can serve as a proxy for forecasting the future availability of CHN data.

### **Data Model and HUC-Equivalent Layers**

The CHN employs a streamlined and efficient data model compared to its predecessor, the NHN. It consists of seven core layers: flowline, flowline\_vaa (value-added attributes), waterbody, catchment, catchment\_aggregate, work\_unit, and hydrolocation.3

For the purpose of creating a watershed identification service analogous to the US system, the key layers are the watershed polygon features:

* **Catchment:** This layer contains the elementary, or fundamental, drainage areas. Each catchment polygon represents the area of land that drains directly into a specific segment of a flowline.  
* **Catchment Aggregate:** This layer is a hierarchical grouping of individual catchments. These aggregates form larger, nested watershed units that are conceptually similar to the nested structure of the US Hydrologic Unit Code (HUC) system.3

These two layers provide the hierarchical structure necessary to replicate the functionality of the US WBD, where users can identify watersheds at different scales.

### **Technical Specifications and Accessibility**

* **Data Model Documentation:** The complete conceptual, logical, and physical data models for the CHN are publicly available in the document "GeoBase Series – CHN: Conceptual, Logical, and Physical Models – Edition 0.2".3 This document is an essential reference for any developer planning to work with CHN data.  
* **Attribute Schema:** The attribute tables are designed for analysis. For example, the catchment\_aggregate table includes a to\_catchment\_aggregate\_code field, which explicitly defines the downstream connectivity to the next catchment aggregate, enabling robust network tracing.3  
* **Coordinate System:** The data is based on the Canadian Spatial Reference System (CSRS), which is an implementation of the North American Datum of 1983 (NAD83).3 This ensures direct spatial compatibility with US WBD data, which is also commonly referenced to NAD83.  
* **Data Access:** CHN data is discoverable and accessible through the federal Open Government Portal (open.canada.ca).4 Access is also provided via ESRI REST services.4 To facilitate data discovery, a generalized index file of all available work units is provided, allowing users to identify and download only the specific geographic areas they need.8  
* **Licensing:** All CHN data is released under the Open Government Licence \- Canada, which is a permissive license allowing for copying, modification, and distribution, including for commercial purposes, making it suitable for use in a public-facing web application.4

### **Verdict for Immediate Cascadia Integration**

The Canadian Hydrospatial Network is unequivocally the ideal *future* data source for this project. Its modern, analysis-ready structure, high-resolution derivation, and explicit design for harmonization with its US counterpart make it the definitive long-term solution.

However, given the complete lack of data coverage for British Columbia at this time, the CHN is **not a viable data source for the immediate implementation** of a Cascadia-wide service. The project must therefore proceed with a robust provincial alternative for the Canadian portion, while architecting the system in a way that facilitates a straightforward migration to the CHN as it becomes available in BC.

#### **Table 1: CHN Watershed Polygon Attribute Schema (Selected Fields)**

This table outlines the key attributes for the CHN catchment and catchment\_aggregate layers, providing a blueprint for future database schema design.

| Table Name | Field Name | Data Type | Description |
| :---- | :---- | :---- | :---- |
| catchment | feature\_id | uuid | Unique feature identifier (Primary Key). |
|  | work\_unit\_code | varchar(7) | Identifier of the work unit the catchment belongs to. |
|  | catchment\_aggregate\_code | varchar(9) | Identifier of the catchment aggregate the catchment belongs to. |
|  | area\_sq\_km | numeric(12,6) | Calculated surface area of the catchment in square kilometers. |
| catchment\_aggregate | feature\_id | uuid | Unique feature identifier (Primary Key). |
|  | catchment\_aggregate\_code | varchar(9) | Unique identifier for the catchment aggregate. |
|  | to\_catchment\_aggregate\_code | varchar(9) | Identifier of the immediate downstream catchment aggregate, enabling network tracing. |
|  | work\_unit\_code | varchar(7) | Identifier of the work unit the aggregate belongs to. |
|  | area\_sq\_km | numeric(12,6) | Calculated surface area of the catchment aggregate in square kilometers. |

Source: Derived from CHN Physical Model specifications.3

## **The Provincial Standard: British Columbia Freshwater Atlas (FWA)**

With the federal CHN not yet available for British Columbia, the project must turn to the authoritative provincial dataset. The British Columbia Freshwater Atlas (FWA) is a mature, high-quality, and comprehensive hydrographic dataset that is the definitive standard for the province and is well-suited for this project's immediate needs.

### **Overview of the FWA as the Authoritative Provincial Source**

The Freshwater Atlas is the official, standardized dataset for mapping all of British Columbia's hydrological features and is managed by GeoBC, a branch of the provincial government.11 It was developed as a significant improvement over the older 1:50,000 scale Watershed Atlas, as the FWA is derived from the province's more detailed 1:20,000 scale TRIM (Terrain Resource Information Management) topographic base maps.11

The FWA provides a fully connected hydrographic network, defining watershed boundaries from heights of land and linking streams, lakes, and wetlands.11 This connected network serves as a robust foundation for sophisticated analysis, modeling, and water resource management, making it far more than just a cartographic product.12

### **Accessing FWA Data: Portals, Services, and Direct Downloads**

The Government of British Columbia provides multiple, open avenues for accessing FWA data, ensuring its availability for a wide range of users, including developers.

* **Primary Portal:** The **BC Data Catalogue** is the modern, official portal for discovering and accessing all FWA datasets. It provides metadata, documentation, and links to various access methods.12  
* **Central Repository:** The data itself is housed in the **BC Geographic Warehouse (BCGW)**, which is the provincial government's central repository for authoritative spatial data.14  
* **Direct FTP Download:** For developers and users requiring bulk data, a public-facing FTP site provides direct access to the entire FWA dataset in File Geodatabase (FGDB) format. This is a highly valuable and efficient access method. The working URL is: ftp://ftp.gdbc.gov.bc.ca/sections/outgoing/bmgs/FWA\_Public/.13  
* **Programmatic Access (Web Services):** Most FWA layers, including watershed polygons, are available as OGC-compliant Web Map Services (WMS) and Web Feature Services (WFS). These services allow for programmatic querying and integration into web applications without the need for bulk data download. The specific service endpoints are discoverable within the metadata records on the BC Data Catalogue.16  
* **Licensing:** FWA data is licensed under the **Open Government Licence \- British Columbia**, a permissive license that allows for the copying, modification, publication, and distribution of the data, including for commercial use, provided attribution is given. This license fully supports the user's intended application.16

### **The FWA Hierarchical System: A Deep Dive into Watershed Codes**

The FWA employs a unique and powerful, albeit complex, hierarchical coding system that is fundamentally different from the area-based system used by the US WBD. The primary identifier is the WATERSHED\_CODE, a 144-character string that encodes the stream network's topology.19

Instead of defining nested geographic areas, the FWA code defines a stream's position within the network. The code for a tributary is generated by concatenating the code of its parent stream with a value representing the proportional distance upstream from the confluence point where the tributary joins.19 This system allows for precise upstream and downstream tracing but means that two adjacent fundamental watersheds will have vastly different codes.

The first three digits of the WATERSHED\_CODE designate one of nine Principal Drainages in the province, providing a high-level geographic grouping.19 For example, all watersheds within the Fraser River basin begin with the code

100, while those in the Columbia River basin begin with 300\.

The structural and conceptual divergence between the FWA's topological coding and the WBD's nested area coding is a critical technical consideration. It makes a simple attribute-based join or the creation of a direct code crosswalk between the two systems impossible. The only common language between the FWA and the WBD is their shared geography. Consequently, the integration strategy must be based on spatial relationships—identifying which FWA watersheds are geographically adjacent to which WBD HUCs at the border—rather than on attempting to translate their incompatible coding schemes. This reality dictates the spatial "stitching" workflow detailed in Section 5\.

### **Identifying the Optimal Dataset: Fundamental vs. Assessment Watersheds**

The FWA offers several distinct watershed polygon layers. Selecting the correct one is crucial for the project's success.

* **FWA Watersheds (Fundamental Watersheds):** This layer represents the smallest, first-order watershed units, with each polygon corresponding to a single stream segment.18 While highly detailed, these units (numbering in the millions) are too granular to serve as an equivalent to the HUC-12 (subwatershed) level and would result in an unwieldy and overly complex service.  
* **FWA Assessment Watersheds:** This layer was specifically created to address the need for a medium-scale unit for regional-level analysis and reporting. These polygons are aggregated from the fundamental watersheds and have a target size of **2,000 to 10,000 hectares**.17 This scale and purpose make them the closest and most appropriate Canadian equivalent to the US WBD's HUC-12 level.

**The FWA Assessment Watersheds dataset is the highly recommended source for this project.** It provides the correct balance of detail and regional scope required for a Cascadia-wide watershed identification service. This dataset is available as a distinct product in the BC Data Catalogue with its own metadata record and download links.12 The document "Overview of Assessment Watersheds" provides essential background on their creation and intended use.21

### **Data Schema, Projections, and Licensing**

* **Format:** The primary bulk download format is **File Geodatabase (FGDB)**, available from the FTP site.16 Other formats like Shapefile or GeoPackage may be available through the BC Data Catalogue's custom download service.  
* **Projection:** The native projection for all FWA data is **BC Albers (EPSG:3005)**.12 This is a standard equal-area projection for the province. For integration with US data, it will be necessary to re-project the FWA data to a common datum and projection, such as NAD83 or WGS84.  
* **Schema:** The attribute table for FWA Assessment Watersheds includes key fields such as ASSESSMENT\_WATERSHED\_ID, the WATERSHED\_CODE of the primary stream within the unit, and area calculations. The full schema can be readily inspected from the downloaded FGDB.

#### **Table 2: Comparison of FWA Watershed Polygon Layers**

| Layer Name | Description | Typical Scale/Size | Analogy to US HUC | Recommendation for this Project |
| :---- | :---- | :---- | :---- | :---- |
| **FWA Fundamental Watersheds** | Smallest drainage unit for a single stream segment. | Very small (often \<100 ha). | More granular than HUC-12. | **Not Recommended.** Too detailed for a regional service. |
| **FWA Assessment Watersheds** | Mesoscale units for regional analysis, aggregated from fundamental watersheds. | 2,000 \- 10,000 ha. | **HUC-12 (Subwatershed)** | **Highly Recommended.** The ideal scale and purpose for this project. |
| **FWA Named Watersheds** | Polygons representing the drainage area for officially named water features. | Highly variable. | No direct analogy. | Not suitable as a primary layer due to inconsistent size. |
| **FWA Watershed Groups** | Large groupings of watersheds, often corresponding to major river basins. | Very large (\>100,000 ha). | HUC-8 (Subbasin) or HUC-6 (Basin). | Too coarse for the intended service level. |

#### **Table 3: BC FWA Principal Drainage Codes**

This table provides a reference for the highest level of the FWA's hierarchical classification system.

| Code | Drainage Name |
| :---- | :---- |
| 100 | Fraser River |
| 200 | Mackenzie River |
| 300 | Columbia River |
| 400 | Skeena River |
| 500 | Nass River |
| 600 | Stikine River |
| 700 | Taku River |
| 800 | Yukon River |
| 9xx | Coastal Rivers (e.g., 900-South Coast, 920-Vancouver Island East) |

Source: Derived from FWA User Guide.19

## **Legacy and Alternative Data Sources**

While the CHN and FWA represent the future and present standards, respectively, a complete assessment requires evaluating legacy and alternative datasets to confirm their suitability.

### **Standard Drainage Area Classification (SDAC)**

The Standard Drainage Area Classification (SDAC) is a legacy federal system developed in 2003 by a partnership including Natural Resources Canada, Environment Canada, and Statistics Canada.22 It provides a three-level hierarchy:

1. **Major Drainage Areas (MDA):** 11 across Canada, draining to major oceans.  
2. **Sub-Drainage Areas:** 164 units.  
3. **Sub-Sub-Drainage Areas (SSDA):** 974 units.24

Crucially, the SDAC was designed primarily as a "unit of statistical aggregation" for reporting purposes, not as a precise, hydrologically-delineated watershed map.24 While related datasets like the "Drainage regions of Canada" (25 regions) are available for download in Shapefile format, they are far too coarse for the project's requirements.26 The full, detailed SDAC polygon dataset is not readily accessible, and its scale and purpose make it fundamentally unsuitable.

**Conclusion:** The SDAC is a legacy statistical framework and is **not appropriate** for this project. It should be disregarded in favor of the more accurate and higher-resolution FWA.

### **Other Federal and Academic Sources**

* **National Hydrographic Network (NHN):** The NHN is the federal dataset that the CHN is in the process of replacing.2 While the NHN was a key input for the IJC's transboundary harmonization work 28, it is now considered outdated for new development. For work within British Columbia, the provincially-managed FWA offers superior resolution, accuracy, and completeness.  
* **British Columbia Ungauged Basin (BCUB) Dataset:** This is a new, open-source academic dataset released in 2023 that provides a comprehensive suite of attributes for over 1.2 million catchments covering BC and its transboundary regions.29 The attributes include detailed information on terrain, soil, land cover, and climate indices, making it an exceptionally powerful resource for hydrological modeling and environmental analysis.29

The BCUB dataset is not a replacement for the FWA as a source of authoritative watershed boundaries for this project's identification purpose. The FWA provides the official delineations. However, the BCUB represents a significant opportunity for future enhancement. Once the unified Cascadia watershed fabric is constructed, the rich attributes from the BCUB dataset could be spatially joined to the final polygons. This would enrich the service immensely, allowing it to provide not just watershed identification but also a wealth of analytical data about each watershed's physical characteristics. The BCUB should be considered a key resource for a "Phase 2" enhancement of the project.

## **The Transboundary Keystone: The International Joint Commission (IJC) Harmonization Project**

The most technically challenging aspect of any cross-border geospatial project is the reconciliation of data at the international boundary. Discrepancies in projection, resolution, attribution, and delineation methodology between national datasets often create significant misalignments. Fortunately, for the Canada-US border, this critical work has already been expertly addressed by the International Joint Commission (IJC).

### **Project Overview and Methodology**

The IJC is an independent binational organization established by the Boundary Waters Treaty of 1909 to manage shared water resources.30 Recognizing the challenge of incompatible hydrographic data, the IJC convened the Transboundary Hydrographic Data Harmonization Task Force in 2008\.28 The task force's goal was to develop a coordinated approach to create a seamless, hydrologically sound binational system by reconciling the US National Hydrography Dataset (NHD) and Watershed Boundary Dataset (WBD) with Canada's National Hydrographic Network (NHN) and its associated drainage areas.28

The harmonization was a multi-phase technical process 28:

* **Phase I:** Focused on matching and reconciling the largest common units: US WBD 8-digit hydrologic units (HUC-8s) with Canada's 4th level Sub-sub-drainage areas (SSDAs).  
* **Phase II:** Harmonized the linear stream networks (NHD and NHN) within those reconciled large-scale units to ensure continuous flow paths across the border.  
* **Phases III & IV:** Created new, higher-resolution "harmonized" drainage areas at the US WBD 10- and 12-digit hydrologic unit levels. This involved delineating new watershed boundaries in the transboundary "swath" that are consistent on both sides of the border.

### **Data Availability and Access**

A critical finding of this research is that the resulting harmonized transboundary data is **not published as a separate, standalone dataset**. Instead, it has been fully reviewed, accepted, and **integrated into the official national datasets of both countries**. Specifically for this project's needs, the harmonized watershed polygons are now distributed as an integral part of the **USGS Watershed Boundary Dataset (WBD)**.28

To access this crucial data, one must simply download the standard WBD from official USGS distribution points, such as The National Map download portal, for the hydrologic regions that straddle the Canada-US border.34 The USGS WBD homepage explicitly provides a link to "US-Canada Transboundary Data Harmonization Information," confirming the integration of this work into the official dataset.34

### **Strategic Importance for the Cascadia Project**

The work completed by the IJC is the keystone for this project. It solves the most difficult and error-prone component of the integration task upfront. Instead of attempting a complex and likely imperfect edge-matching exercise between the BC FWA and the US WBD, developers can treat the IJC-harmonized portion of the WBD as a single, contiguous block of authoritative data for the entire border region.

This fundamentally changes the nature of the integration problem. It is no longer a border-matching exercise but a more manageable data-appending task. The primary effort shifts from reconciling the international boundary to simply "stitching" the interior of British Columbia (using the FWA) to the northern, inland edge of this pre-harmonized transboundary block. This dramatically reduces project risk, complexity, and development time.

## **A Unified Cascadia Watershed Fabric: Integration and Harmonization Strategy**

With a clear understanding of the available datasets and their respective roles, a practical, multi-step strategy can be formulated to construct a seamless and authoritative watershed fabric for the Cascadia bioregion. This strategy is designed to be immediately implementable while remaining adaptable for future data improvements.

### **Recommended Hybrid Data Architecture**

The most robust and efficient strategy is a three-tiered, hybrid approach that uses the most authoritative data available for each distinct geographic domain. This avoids the pitfalls of trying to force a single, less-accurate dataset to cover the entire region.

1. **United States Domain:** For all watersheds located entirely within the US portion of Cascadia, the standard **USGS Watershed Boundary Dataset (WBD)** is the sole source of truth.  
2. **Transboundary Domain:** For all watersheds that physically straddle the international boundary, the **IJC-harmonized polygons contained within the USGS WBD** are the non-negotiable, authoritative source. This data provides the "golden stitch" connecting the two national systems.  
3. **Canadian Interior Domain:** For all watersheds located entirely within British Columbia, the **BC Freshwater Atlas (FWA) Assessment Watersheds** dataset is the authoritative source.

This architecture ensures that every polygon in the final dataset is derived from the best available source for its specific location.

### **Harmonizing FWA with the HUC System: A Technical Workflow**

The core development task is to integrate the BC FWA data with the WBD/IJC data. As established, this must be a spatial process. The following workflow outlines the necessary steps:

**Step 1: Data Acquisition and Preparation**

* Acquire the three data components: the full WBD for the relevant US states (WA, ID, MT), which includes the IJC-harmonized units, and the FWA Assessment Watersheds for British Columbia.  
* Re-project all datasets into a single, common coordinate system suitable for the Cascadia region. A custom Albers Equal Area projection centered on the region is recommended to minimize distortion for area calculations, but a standard system like WGS 84 / UTM Zone 10N (EPSG:32610) would also be effective.

**Step 2: Isolate the Canadian "Stitching Edge"**

* From the WBD, select all polygons that have been influenced by the IJC harmonization process. These can typically be identified by their location or specific attributes indicating their transboundary nature.  
* From this selection, identify the subset of polygons that share a boundary with Canada. This set of polygons forms the northern, inland edge of the US/transboundary block—the target to which the FWA data will be joined.

**Step 3: Identify Upstream FWA Watersheds**

* Using geospatial analysis tools, perform a spatial join or adjacency analysis. The goal is to identify every FWA Assessment Watershed that either directly touches one of the "stitching edge" IJC polygons or is upstream of a watershed that does. This process identifies the entire contributing area from the FWA dataset that flows into the transboundary system.

**Step 4: Create a Unified Identification System**

* To create a seamless service, a new, unified primary key must be generated for every polygon in the combined dataset. This ID should be structured to be unique and to indicate the provenance of the data. A recommended format is a prefixed string:  
  * **Example for a standard US HUC:** CASC\_ID \= 'US-170101010101'  
  * **Example for an IJC-harmonized HUC:** CASC\_ID \= 'IJC-171100040101'  
  * **Example for a BC FWA Assessment Watershed:** CASC\_ID \= 'BC-300-589976' (using a native FWA identifier)  
* This approach preserves the original, native identifiers from each source dataset for traceability while providing a consistent key for the application.

**Step 5: Build the Topological Links**

* This is the most critical step for enabling cross-border network analysis. A new field, Downstream\_CASC\_ID, must be created.  
* For every FWA Assessment Watershed identified in Step 3 that flows directly into an IJC-harmonized unit, this field must be populated with the CASC\_ID of the corresponding downstream IJC polygon.  
* Within the FWA and WBD datasets, similar downstream links can be established using their native topological attributes. This process digitally "stitches" the entire network together, allowing an application to trace water flow from a headwater stream in interior British Columbia, across the border, and down to the Pacific Ocean.

### **Proposed Unified Data Schema**

The following table provides a blueprint for the final, integrated database schema. It harmonizes attributes from the disparate source datasets into a clean, consistent structure.

#### **Table 4: Proposed Unified Schema for the Cascadia Watershed Fabric**

| Field Name | Data Type | Description | Source Data Mapping |
| :---- | :---- | :---- | :---- |
| **CASC\_ID** | String | **Primary Key.** The new, unified identifier for each watershed polygon. | Generated during integration (Step 4). |
| **Native\_ID** | String | The original identifier from the source dataset. | WBD: HUC12; FWA: ASSESSMENT\_WATERSHED\_ID. |
| **Watershed\_Name** | String | The common name of the watershed. | WBD: Name; FWA: GNIS\_NAME or similar. |
| **Area\_SqKm** | Double | Area of the polygon in square kilometers, calculated in an equal-area projection. | WBD: AreaSqKm; FWA: FEATURE\_AREA\_SQM / 1,000,000. |
| **DataSource** | String | Indicates the origin of the data ('WBD', 'IJC-WBD', 'BC-FWA'). | Assigned during integration. |
| **HUC\_Code** | String | The official Hydrologic Unit Code. Populated only for US and IJC units. | WBD: HUC12. Null for FWA units. |
| **FWA\_Code** | String | The official FWA Watershed Code. Populated only for BC units. | FWA: WATERSHED\_CODE. Null for WBD units. |
| **Downstream\_CASC\_ID** | String | **Topological Link.** The CASC\_ID of the immediate downstream polygon. | Generated during integration (Step 5). |
| **Province\_State** | String | The primary province or state the polygon resides in. | Derived spatially from administrative boundaries. |

### **Long-Term Strategy: Migration to the Canadian Hydrospatial Network (CHN)**

The architecture described above is designed for longevity. When CHN data becomes available for British Columbia, the migration path is clear and manageable. The process would involve replacing the DataSource \= 'BC-FWA' polygons with the corresponding CHN Catchment Aggregate polygons.

Because the CHN is being designed for alignment with the USGS 3DHP (the WBD's successor), this future migration will be far simpler than the initial integration. The CASC\_ID and Downstream\_CASC\_ID fields for the Canadian portion would be updated to reflect the CHN's native identifiers and topological links. The fundamental hybrid architecture and unified schema would remain valid, protecting the initial development investment.

## **Conclusions and Final Recommendations**

This comprehensive assessment confirms that the development of a unified, cross-border watershed identification service for the Cascadia bioregion is not only possible but can be built upon a foundation of high-quality, authoritative, and openly licensed government data. The primary technical challenge is not a scarcity of data, but the methodical integration of three distinct and robust datasets into a single, coherent hydrographic fabric. The extensive harmonization work already completed by the International Joint Commission significantly mitigates the complexity of this task.

To ensure the successful and efficient implementation of this project, the following recommendations are made:

1. **Adopt the Hybrid Data Architecture:** Proceed immediately with the three-tiered data strategy outlined in this report. Use the USGS WBD for the US interior, the IJC-harmonized portion of the WBD for the transboundary region, and the BC Freshwater Atlas for the interior of British Columbia. This approach leverages the most authoritative data for each domain.  
2. **Prioritize the FWA Assessment Watersheds:** For the British Columbia component, the FWA Assessment Watersheds dataset is the correct choice. Its scale, purpose, and provincial authority make it the ideal Canadian analogue to the US HUC-12 subwatersheds.  
3. **Leverage the IJC-Harmonized WBD as the Keystone:** Treat the IJC-harmonized data, accessible through the standard USGS WBD, as the definitive and non-negotiable source for all watersheds that cross the international boundary. This eliminates the need for complex and error-prone border-matching and provides the "golden stitch" for the unified fabric.  
4. **Implement the Spatial Integration Workflow:** Follow the detailed technical workflow presented in Section 5\. The creation of a unified identification system (CASC\_ID) and, most importantly, a unified topological network (Downstream\_CASC\_ID) is essential for the service's core functionality of cross-border tracing.  
5. **Plan for the Future with a CHN Migration Path:** Architect the system using the proposed unified schema. This schema is designed to be forward-compatible with the Canadian Hydrospatial Network. The project should include a long-term plan to migrate the Canadian data component from the FWA to the CHN once it becomes available for British Columbia. Monitoring the progress of NRCan's CHN and HRDEM programs will provide the necessary roadmap for this future enhancement, ensuring the system remains current and authoritative for years to come.

#### **Works cited**

1. The New Canadian Hydrospatial Network (CHN) – Advancements in Hydrography for Improved Modelling | Schedule | GeoIgnite 2025 \- Browser not Supported, accessed June 18, 2025, [https://sites.grenadine.co/sites/gogeomatics/en/geoignite-2025/schedule/21437/The%20New%20Canadian%20Hydrospatial%20Network%20%28CHN%29%20%E2%80%93%20Advancements%20in%20Hydrography%20for%20Improved%20Modelling?signups=0\&tags=47\&updated=0\&view\_setting=calendar](https://sites.grenadine.co/sites/gogeomatics/en/geoignite-2025/schedule/21437/The%20New%20Canadian%20Hydrospatial%20Network%20%28CHN%29%20%E2%80%93%20Advancements%20in%20Hydrography%20for%20Improved%20Modelling?signups=0&tags=47&updated=0&view_setting=calendar)  
2. The New Canadian Hydrospatial Network (CHN) | Schedule | Events, accessed June 18, 2025, [https://sites.grenadine.co/sites/gogeomatics/ar/schedule/21146](https://sites.grenadine.co/sites/gogeomatics/ar/schedule/21146)  
3. Canadian Hydrospatial Network (CHN) Data Model Edition 0.2 2025 ..., accessed June 18, 2025, [ftp://ftp.geogratis.gc.ca/pub/nrcan\_rncan/vector/chn\_rhc/doc/CHN\_GeoBase\_Series\_Data\_Models\_EN\_V\_0\_2.pdf](ftp://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/chn_rhc/doc/CHN_GeoBase_Series_Data_Models_EN_V_0_2.pdf)  
4. Canadian Hydrospatial Network \- CHN \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb](https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb)  
5. Canadian Hydrospatial Network \- Natural Resources Canada, accessed June 18, 2025, [https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-portals-tools-services/canadian-hydrospatial-network](https://natural-resources.canada.ca/science-data/data-analysis/geospatial-data-portals-tools-services/canadian-hydrospatial-network)  
6. Canadian Hydrospatial Network (CHN) \- GEO.CA, accessed June 18, 2025, [https://geo.ca/initiatives/geobase/canadian-hydrospatial-network/](https://geo.ca/initiatives/geobase/canadian-hydrospatial-network/)  
7. The Government of Canada is investing in flood mapping and adaptation projects, accessed June 18, 2025, [https://www.newswire.ca/news-releases/the-government-of-canada-is-investing-in-flood-mapping-and-adaptation-projects-812846276.html](https://www.newswire.ca/news-releases/the-government-of-canada-is-investing-in-flood-mapping-and-adaptation-projects-812846276.html)  
8. Canadian Hydrospatial Network \- CHN \- GEO.CA Viewer, accessed June 18, 2025, [https://app.geo.ca/result/en/canadian-hydrospatial-network---chn?id=ae385105-e48c-4b54-bd0f-dfb7303301cb\&lang=en](https://app.geo.ca/result/en/canadian-hydrospatial-network---chn?id=ae385105-e48c-4b54-bd0f-dfb7303301cb&lang=en)  
9. Watershed Boundary Dataset (WBD) Transitioning to 3DHP \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/media/videos/watershed-boundary-dataset-wbd-transitioning-3dhp](https://www.usgs.gov/media/videos/watershed-boundary-dataset-wbd-transitioning-3dhp)  
10. Canadian Hydrospatial Network \- CHN \- CHN Index of Available Files (English) \- work unit boundaries and grades \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb/resource/35140a43-c516-455d-a54a-3918a0947b53](https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb/resource/35140a43-c516-455d-a54a-3918a0947b53)  
11. Freshwater Atlas \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa\_exec\_summary.pdf](https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa_exec_summary.pdf)  
12. Freshwater Atlas \- Province of British Columbia \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/freshwater](https://www2.gov.bc.ca/gov/content/data/geographic-data-services/topographic-data/freshwater)  
13. British Columbia Freshwater Atlas Features, IW Study Area \- Data Basin, accessed June 18, 2025, [https://databasin.org/datasets/25c20e4a151c4af4956583c4047c03d8/](https://databasin.org/datasets/25c20e4a151c4af4956583c4047c03d8/)  
14. BC Geographic Warehouse | data-publication, accessed June 18, 2025, [https://bcgov.github.io/data-publication/pages/dps\_bcgw.html](https://bcgov.github.io/data-publication/pages/dps_bcgw.html)  
15. BC Geographic Warehouse \- Province of British Columbia, accessed June 18, 2025, [https://www2.gov.bc.ca/gov/content/data/finding-and-sharing/bc-geographic-warehouse](https://www2.gov.bc.ca/gov/content/data/finding-and-sharing/bc-geographic-warehouse)  
16. Freshwater Atlas Stream Network \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/92344413-8035-4c08-b996-65a9b3f62fca](https://open.canada.ca/data/en/dataset/92344413-8035-4c08-b996-65a9b3f62fca)  
17. Freshwater Atlas Assessment Watersheds \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/97d8ef37-b8d2-4c3b-b772-6b25c1db13d0](https://open.canada.ca/data/en/dataset/97d8ef37-b8d2-4c3b-b772-6b25c1db13d0)  
18. Freshwater Atlas Watersheds \- Open Government Portal \- Canada.ca, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/3ee497c4-57d7-47f8-b030-2e0c03f8462a](https://open.canada.ca/data/en/dataset/3ee497c4-57d7-47f8-b030-2e0c03f8462a)  
19. Freshwater Water Atlas User Guide \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa\_user\_guide.pdf](https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa_user_guide.pdf)  
20. Freshwater Atlas Watersheds \- Fisheries Map Gallery \- ArcGIS Online, accessed June 18, 2025, [https://fisheries-map-gallery-crm.hub.arcgis.com/datasets/governmentofbc::freshwater-atlas-watersheds](https://fisheries-map-gallery-crm.hub.arcgis.com/datasets/governmentofbc::freshwater-atlas-watersheds)  
21. Assessment Watersheds for Regional Level Applications \- Gov.bc.ca, accessed June 18, 2025, [https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa\_overview\_of\_assessment\_watersheds.pdf](https://www2.gov.bc.ca/assets/gov/data/geographic/topography/fwa/fwa_overview_of_assessment_watersheds.pdf)  
22. Standard Drainage Area Classification (SDAC) 2003 \- Statistique Canada, accessed June 18, 2025, [https://www23.statcan.gc.ca/imdb/p3VD.pl?Function=getVD\&TVD=134769](https://www23.statcan.gc.ca/imdb/p3VD.pl?Function=getVD&TVD=134769)  
23. Standard Drainage Area Classification (SDAC) 2003, accessed June 18, 2025, [https://www.statcan.gc.ca/en/subjects/standard/sdac/sdac](https://www.statcan.gc.ca/en/subjects/standard/sdac/sdac)  
24. Atlas of Canada \- Major Drainage Areas of Canada \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/74eb52a9-c088-401c-bfb3-f08a18899e7b](https://open.canada.ca/data/en/dataset/74eb52a9-c088-401c-bfb3-f08a18899e7b)  
25. Canadian Drainage Areas \- Atlas of Canada, accessed June 18, 2025, [https://atlas.gc.ca/drainage-areas/Atlas\_Drainage\_Areas\_EN.html?\_gl=1\*1wbttoy\*\_ga\*MzkzNDA3OTIuMTY4MjcwMjc2MQ..\*\_ga\_C2N57Y7DX5\*MTc0MTYzMzMxNy4xMjYuMS4xNzQxNjM0MTM5LjAuMC4w](https://atlas.gc.ca/drainage-areas/Atlas_Drainage_Areas_EN.html?_gl=1*1wbttoy*_ga*MzkzNDA3OTIuMTY4MjcwMjc2MQ..*_ga_C2N57Y7DX5*MTc0MTYzMzMxNy4xMjYuMS4xNzQxNjM0MTM5LjAuMC4w)  
26. Drainage regions of Canada \- Open Government Portal, accessed June 18, 2025, [https://open.canada.ca/data/en/dataset/b1c2dffa-c2ba-4d0e-b803-a483eef0f579](https://open.canada.ca/data/en/dataset/b1c2dffa-c2ba-4d0e-b803-a483eef0f579)  
27. National Hydrographic Network (NHN) Watershed Boundary \- Leddy Library, accessed June 18, 2025, [https://leddy.uwindsor.ca/national-hydrographic-network-nhn-watershed-boundary](https://leddy.uwindsor.ca/national-hydrographic-network-nhn-watershed-boundary)  
28. Data harmonization | International Joint Commission, accessed June 18, 2025, [https://ijc.org/en/iwi-iibh/data-harmonization](https://ijc.org/en/iwi-iibh/data-harmonization)  
29. BCUB – a large-sample ungauged basin attribute dataset for British Columbia, Canada, accessed June 18, 2025, [https://essd.copernicus.org/articles/17/259/2025/](https://essd.copernicus.org/articles/17/259/2025/)  
30. TRANSBOUNDARY COLUMBIA INITATIVES, BY SCALE (International, Regional, Provincial, State, Tribal), accessed June 18, 2025, [https://transboundarywaters.ceoas.oregonstate.edu/sites/transboundarywaters.ceoas.oregonstate.edu/files/TransboundaryColumbiaInitiatives\_Timboe\_Database.pdf](https://transboundarywaters.ceoas.oregonstate.edu/sites/transboundarywaters.ceoas.oregonstate.edu/files/TransboundaryColumbiaInitiatives_Timboe_Database.pdf)  
31. Hydrographic Data Harmonization Support \- International Joint Commission, accessed June 18, 2025, [https://www.ijc.org/en/hydrographic-data-harmonization-support](https://www.ijc.org/en/hydrographic-data-harmonization-support)  
32. USGS National Hydrography Dataset Newsletter \- AWS, accessed June 18, 2025, [https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/NHDNewsletter\_17\_10\_Oct18.pdf](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/NHDNewsletter_17_10_Oct18.pdf)  
33. More Shared Waters Being Matched Up in Binational Mapping Project, accessed June 18, 2025, [https://www.ijc.org/en/more-shared-waters-being-matched-binational-mapping-project](https://www.ijc.org/en/more-shared-waters-being-matched-binational-mapping-project)  
34. Watershed Boundary Dataset | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/watershed-boundary-dataset](https://www.usgs.gov/national-hydrography/watershed-boundary-dataset)  
35. Access National Hydrography Products | U.S. Geological Survey \- USGS.gov, accessed June 18, 2025, [https://www.usgs.gov/national-hydrography/access-national-hydrography-products](https://www.usgs.gov/national-hydrography/access-national-hydrography-products)