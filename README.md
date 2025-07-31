# aadr-visualizer

This repository contains data and scripts that were used in the Allen Ancient DNA Resource (AADR) Metadata ETL Python Pipeline to generate the final CSV file imported into the AADR Visualizer (https://arcg.is/1CyL5n). 

AADR Visualizer 
v1.0 (Updated: 05-15-2025) - uses AADR v62.0
v1.1 (Updated: 07-31-2025) - edited region/sub-region for eastern Russia, St. Martin's, and Guam

## Scripts 

`aadr_visualizer_v62.py`: Script using files in data/ to create the final CSV.
    
`doi_availability.py`: Script to check hyperlinks generated for each DOI.

## Result files

`doi_link_check_v62.csv`: Spreadsheet of all hyperlinks and whether it was successful, produced from `doi_availability.py`.
    
`aadr_noRefPresent_v62.csv`: Final CSV imported into the AADR Visualizer, produced from `aadr_visualizer_v62.py`.
    
## Input data files

`data/countries.csv`: Spreadsheet containing standardized list of countries (ISO-3166, v10.0, https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes.git), with associated country codes, regions, and sub-regions. 
    
`data/manual_edit_notes_v62.csv`: Spreadsheet to track additional notes for provided genetic IDs.
    
`data/missing_doi_v62.csv`: Spreadsheet created to track provide missing DOIs and related notes for provided publication codes.

`data/missing_lat_lon_v62.csv`: Spreadsheet created to track manually edited coordinates (GISLat and GISLon) and related notes for provided localities.
    
`data/v62.0_1240k_public.anno`: Original ANNO file from the AADR.

`data/Region_Subregion_list.csv`: Spreadsheet tracking manually edited region and sub-region for select samples in transcontinental countries.

## Contact
Please email Dr. Melinda A. Yang at myang@richmond.edu with questions or comments.
