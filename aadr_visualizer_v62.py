import pandas as pd
class AadrCheck:
    def __init__(self, aadr_filepath):
        self.file = aadr_filepath
        self.aadr_df = self.read_aadr_file()
        
    def process_aadr_file(self):
        # remove references
        refs = self.clean_refs() # 4 rows removed

        # remove presents
        presents = self.clean_presents() # 4054 rows removed

        if len(self.aadr_df) == 17629 - len(refs) - len(presents): #v62: 13571
            return 1 # all set, good to go
        else:
            return 0 # there is a missing row

    def merge_lat_lon(self, missing_lat_lon_filepath):
        missing_lat_lon = pd.read_csv(missing_lat_lon_filepath, delimiter=",", header=0, dtype=str)

        merged_df = self.aadr_df.merge(missing_lat_lon, on='locality', how='left')
        merged_df['GISLat'] = merged_df['lat'].fillna(merged_df['GISLat'])
        merged_df['GISLon'] = merged_df['lon'].fillna(merged_df['GISLon'])
        
        # update aadr_df
        self.aadr_df = merged_df

        # check empty lat/lon
        empty_lat_lon = self.aadr_df[(self.aadr_df["GISLat"].isnull()) | (self.aadr_df["GISLon"].isnull())]
        return empty_lat_lon

    def merge_regions(self, region_filepath, missing_region_filepath):
        region_df = pd.read_csv(region_filepath, delimiter=",", header=0, dtype=str)    
        region_df = region_df[['name', 'region', 'sub-region']]

        missing_region_df = pd.read_csv(missing_region_filepath, delimiter=",", header=0, dtype=str)
        merged_region_df = region_df.merge(missing_region_df, on="name", how='outer')
        merged_region_df['edited_name'] = merged_region_df['edited_name'].fillna(merged_region_df['name'])
        merged_region_df['region'] = merged_region_df['region'].fillna(merged_region_df['missing_region'])
        merged_region_df['sub-region'] = merged_region_df['sub-region'].fillna(merged_region_df['missing_subregion'])
        merged_region_df.drop(columns=['name', 'missing_region', 'missing_subregion'], inplace=True)

        merged_df = self.aadr_df.merge(merged_region_df, left_on="political_entity", right_on="edited_name", how='left')
        merged_df.drop(columns=['edited_name'], inplace=True)

        # update aadr_df
        self.aadr_df = merged_df

        # check empty political entities
        empty_regions = self.aadr_df[self.aadr_df["region"].isnull() | self.aadr_df["sub-region"].isnull()]

        return empty_regions

    def merge_doi(self, missing_doi_filepath):        
        self.aadr_df[['publication_code', 'publication_note']] = self.aadr_df['publication'].str.extract(r'^(.*?)\s*(?:\((.*?)\))?$')
        
        doi_df = pd.read_csv(missing_doi_filepath, delimiter=",", header=0, dtype=str)
        
        merged_df = self.aadr_df.merge(doi_df, on='publication_code', how='left')
        merged_df['doi_link'] = merged_df['doi_link'].fillna(merged_df['doi'])

        def format_doi(val):
            if pd.isna(val):
                return None
            val = val.strip()
            if val.startswith("https://doi.org/"):
                return val
            elif val.startswith("doi:"):
                return "https://doi.org/" + val[4:].strip()
            elif val.startswith("10."):
                return "https://doi.org/" + val
            elif val.startswith("doi.org/"):
                return "https://" + val
            else:
                return val
    
        merged_df["doi_link"] = merged_df["doi_link"].apply(format_doi)
        merged_df.loc[merged_df["doi"].notna(), "doi_notes"] = None

        # update aadr_df
        self.aadr_df = merged_df
        self.aadr_df.drop(columns=['publication_code', 'publication_note'], inplace=True)

        # check empty doi links
        empty_doi_link = self.aadr_df[self.aadr_df["doi_link"].isnull()]
        return empty_doi_link

    
    def read_aadr_file(self):
        columns_mapping = {
            0: "genID", 1: "masterID", 5: "publication", 6: "doi", 7:"repository",
            9: "ybp", 11: "yrange", 13: "groupID", 14: "locality", 15: "political_entity",
            16: "lat", 17: "lon", 19: "sequence_type", 22: "snpauto", 24: "molsex",
            27: "yhaplo_term", 28: "yhaplo_isogg", 30: "mtDNA_covg", 31: "mtDNA_haplo",
            33: "dmgrate", 37: "libtype", 40: "asm"
        }
        
        aadr_df = pd.read_csv(
            self.file, delimiter="\t", usecols=list(columns_mapping.keys()),
            names=columns_mapping.values(), header=0, na_values="..", dtype = str
        )
        
        # reorder
        aadr_df = aadr_df[['genID', 'masterID', 'groupID', 'publication', 'doi', 'ybp', 'yrange',
                           'locality', 'political_entity', 'lat', 'lon', 'snpauto', 'molsex',
                           'yhaplo_term', 'yhaplo_isogg', 'mtDNA_covg', 'mtDNA_haplo',
                           'dmgrate', 'libtype', 'asm', 'repository', 'sequence_type']]
        
        return aadr_df
    
    def clean_refs(self):
        ref_lst = ["Ancestor.REF", "Chimp.REF", "Gorilla.REF", "Href.REF"]
        ref_df = self.aadr_df[self.aadr_df["genID"].isin(ref_lst)]
        self.aadr_df = self.aadr_df[~self.aadr_df["genID"].isin(ref_lst)]
        return ref_df
    
    def clean_presents(self):
        present_df = self.aadr_df[self.aadr_df["yrange"] == "present"]
        self.aadr_df = self.aadr_df[self.aadr_df["yrange"] != "present"]
        return present_df

    def clean_notes(self, manual_edit_filepath):
        manual_df = pd.read_csv(manual_edit_filepath, delimiter=",", header=0, dtype=str)
        merged_df = self.aadr_df.merge(manual_df, on='genID', how='left')
        self.aadr_df = merged_df
        self.aadr_df["notes"] = self.aadr_df[["doi_notes", "lat_lon_notes", "region_notes", "manual_notes"]].agg(lambda x: ', '.join(x.dropna()), axis=1)
        self.aadr_df.drop(columns=["doi_notes", "lat_lon_notes", "region_notes", "manual_notes"], inplace=True)
  
    def clean_sequence_type(self):
        mask = self.aadr_df['sequence_type'].isin(['AG, BY, AA'])
        self.aadr_df.loc[mask, 'sequence_type'] = 'AG.BY.AA'
        mask = self.aadr_df['sequence_type'].isin(['AG,SG', 'SG, AG'])
        self.aadr_df.loc[mask, 'sequence_type'] = 'AG.SG'
        return self.aadr_df['sequence_type'].unique().tolist()
    
    def exc_regions(self, region_exception_filename, region, subregion, region_note):
        exc_region_df = pd.read_csv(region_exception_filename, delimiter=",", header=0, dtype=str)
        exc_region_list = exc_region_df["genID"].unique().tolist()
        mask = self.aadr_df['genID'].isin(exc_region_list)
        self.aadr_df.loc[mask, 'region'] = region
        self.aadr_df.loc[mask, 'sub-region'] = subregion
        self.aadr_df.loc[mask, 'region_notes'] = region_note
        
    def save_aadr_df(self, aadr_csv_filename):
        self.aadr_df.to_csv(aadr_csv_filename, index=False)

def main():
    aadr_filepath = "data/v62.0_1240k_public.anno"
    region_filepath = "data/iso_country_v10.0.csv"
    missing_region_filepath = "data/missing_region_v62.csv"
    missing_lat_lon_filepath = "data/missing_lat_lon_v62.csv"
    missing_doi_filepath = "data/missing_doi_v62.csv"
    manual_edit_filepath = "data/manual_edit_notes_v62.csv"
    aadr_csv_filename = "aadr_noRefPresent_v62.csv"

    aadr = AadrCheck(aadr_filepath)

    # remove refs/present-day popns
    print(aadr.process_aadr_file())
 
    # edit sequence type
    seq_type = aadr.clean_sequence_type()
    if len(seq_type) != 12:
        print(seq_type)
    
    # merge lat/lon
    lat_lon = aadr.merge_lat_lon(missing_lat_lon_filepath)
    if not lat_lon.empty: # 1 missing lat/lon
        print("locality(missing lat/lon):", lat_lon['locality'].unique().tolist())
        # print(lat_lon[['genID', 'masterID','locality', 'lat', 'lon']])

    # merge regions    
    regions = aadr.merge_regions(region_filepath, missing_region_filepath)
    region_list1 = "data/Americas_LAC_list.csv"
    region_list2 = "data/Oceania_Micronesia_list.csv"
    region_list3 = "data/Asia_Siberia_list.csv"
    region_note = "Assigned region/subregion manually because the political entity is a transcontinental state."
    aadr.exc_regions(region_list1, "Americas", "Latin America and the Caribbean", region_note)
    aadr.exc_regions(region_list2, "Oceania", "Micronesia", region_note)
    aadr.exc_regions(region_list3, "Asia", "Siberia", region_note)   
    if not regions.empty:
        # print("region:", regions['political_entity'].unique().tolist())
        print(regions[['genID', 'masterID', 'political_entity', 'region', 'sub-region', 'region_notes']])
        
    # edit publications
    publications = aadr.merge_doi(missing_doi_filepath)
    if not publications.empty:
        print("publication(missing doi):", publications['publication'].unique().tolist())
        # print(publications[['genID', 'masterID', 'publication']])
        
    # edit notes
    aadr.clean_notes(manual_edit_filepath)
    
    # save aadr csv
    aadr.save_aadr_df(aadr_csv_filename)

if __name__ == "__main__":    
    main()