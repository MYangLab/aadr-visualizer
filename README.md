# aadr-visualizer

This repository contains data and scripts that were used in the Allen Ancient DNA Resource (AADR) Metadata ETL Python Pipeline to generate the final CSV file imported into the AADR Visualizer (https://arcg.is/1CyL5n). 

AADR Visualizer v1.0 (Update: 05-16-2025) - uses AADR v62.0


Scripts include the following: 
    - aadr_visualizer_v62.py: Script using files in data/ to create the final CSV
    - doi_availability.py: Script to check hyperlinks generated for each DOI

Results include the following:
    - doi_link_check_v62.csv: Spreadsheet of all hyperlinks and whether it was successful
    - aadr_noRefPresent_v62.csv: Final CSV imported into the AADR Visualizer
    
Original data files include the following:
    - data/countries.csv: Spreadsheet containing standardized list of countries (ISO-3166, v10.0, https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes.git), with associated country codes, regions, and sub-regions. 
    - data/manual_edit_notes_v62.csv: Spreadsheet to track additional notes for provided genetic IDs.
    - data/missing_doi_v62.csv: Spreadsheet created to track provide missing DOIs and related notes for provided publication codes.
    - data/missing_lat_lon_v62.csv: Spreadsheet created to track manually edited coordinates (GISLat and GISLon) and related notes for provided localities.
    - data/v62.0_1240k_public.anno: Original ANNO file from the AADR.