import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
import laspy
from osgeo import osr

# Function to get CRS options
def get_crs_options():
    crs_options = []
    srs = osr.SpatialReference()
    for i in range(srs.GetEPSGGeogCSCount()):
        srs.ImportFromEPSG(i)
        crs_options.append(srs.GetAttrValue("AUTHORITY", 1))
    return crs_options

# Function to merge LAS files
def merge_las_files():
    # Open file dialog to select input LAS files
    input_files = filedialog.askopenfilenames(filetypes=(("LAS Files", "*.las"), ("All files", "*.*")))

    # Get output file name
    output_file = filedialog.asksaveasfilename(defaultextension=".las", filetypes=(("LAS Files", "*.las"), ("All files", "*.*")))

    # Check if any files were selected
    if not input_files:
        return

    # Create an empty point cloud to hold merged data
    merged_points = None

    # Get selected CRS from the dropdown menu
    selected_crs = crs_combobox.get()

    # Create an empty SpatialReference object for the selected CRS
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(selected_crs))

    # Loop through each input file
    for file_path in input_files:
        # Open LAS file
        las = laspy.read(file_path)

        # Set the CRS of the LAS file
        las.header.set_srs(srs)

        # Get point data from LAS file
        points = np.vstack((las.x, las.y, las.z, las.red, las.green, las.blue)).T

        # Concatenate point data to the merged point cloud
        if merged_points is None:
            merged_points = points
        else:
            merged_points = np.concatenate((merged_points, points))

    # Create a new LAS file for merged data
    merged_las = laspy.create(file_version=las.header.version, point_format=las.header.point_format)

    # Set merged point data in the new LAS file
    merged_las.x = merged_points[:, 0]
    merged_las.y = merged_points[:, 1]
    merged_las.z = merged_points[:, 2]
    merged_las.red = merged_points[:, 3].astype(np.uint16)
    merged_las.green = merged_points[:, 4].astype(np.uint16)
    merged_las.blue = merged_points[:, 5].astype(np.uint16)

    # Update header information
    merged_las.header.point_count = len(merged_points)

    # Save the merged LAS file
    merged_las.write(output_file)

    # Display a success message
    messagebox.showinfo("Merge Complete", "LAS files have been merged successfully.")

# Create the GUI window
window = tk.Tk()
window.title("LAS File Merger")

# Get the CRS options
crs_options = get_crs_options()

# Create a dropdown menu for selecting the CRS
crs_label = tk.Label(window, text="Select CRS:")
crs_label.pack()

crs_combobox = ttk.Combobox(window, values=crs_options)
crs_combobox.current(0)
crs_combobox.pack(pady=5)

# Add a button to merge LAS files
merge_button = tk.Button(window, text="Merge LAS Files", command=merge_las_files)
merge_button.pack(pady=10)

# Startthe GUI event loop
window.mainloop()
