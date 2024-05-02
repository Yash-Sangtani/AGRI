from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np
import os
"""
Using bs4 to etract the plot and farmer information from the cane up website. 
UGC CODE AND effective area in the csv file.
"""
#creating all_html_files

# Directory containing HTML files
html_files_directory = './Data/ugc_scrape/__MACOSX/ugc_scrape'

# Get a list of all files in the directory
all_files = os.listdir(html_files_directory)

# Filter HTML files
html_files = [file for file in all_files if file.endswith('.txt')]

# Create full file paths
all_html_files = [os.path.join(html_files_directory, file) for file in html_files]

unique_plot_counts=0
ugc_codes=[]
effective_area=[]
for file_path in tqdm(all_html_files):

    ugc_code=file_path.split("/")[-1].split(".")[0]

    # Read HTML content from a file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the span element with the specified id
    span_element = soup.find('span', id='LblGenlIncrease')

    # Extract the text and isolate the number
    extracted_text = span_element.get_text() if span_element else None
    total_area = extracted_text.split()[0] if extracted_text else None

    if total_area :
        buffer_area=float(total_area)+2


        # Find all td elements with class="grid1Area"
        grid1_area_elements = soup.find_all('td', class_='grid1Area')

        # Extract and print the numbers
        table_numbers = [element.text.strip() for element in grid1_area_elements if element.text.strip().replace('.', '').isdigit()]
        table_numbers=[float(x) for x in table_numbers]
        plot_areas=[x for x in table_numbers if x<=buffer_area]
        number_plot=len(plot_areas)-1

        if number_plot==1:
            unique_plot_counts+=1
            ugc_codes.append(ugc_code)
            effective_area.append(total_area)

print("Plots with count == 1")
print(unique_plot_counts)
data = np.array([ugc_codes, effective_area])
data = pd.DataFrame(data, columns=["ugc_code", "effective_area"])
data.to_csv("Data/ugc.csv", index=False)