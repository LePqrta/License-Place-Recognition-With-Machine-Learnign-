import numpy as np
from skimage.transform import resize
from skimage.filters import threshold_otsu
from skimage import measure
from skimage.measure import regionprops
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import cca


license_plate = 255 - cca.plate_like_objects[2] 


gray_plate = cca.plate_like_objects[2]
thresh = threshold_otsu(gray_plate)
binary_plate = gray_plate > thresh
license_plate = np.logical_not(binary_plate)
labelled_plate = measure.label(license_plate)

fig, ax1 = plt.subplots(1)
ax1.imshow(license_plate, cmap="gray")

character_dimensions = (0.35*license_plate.shape[0], 0.60*license_plate.shape[0], 0.05*license_plate.shape[1], 0.15*license_plate.shape[1])
min_height, max_height, min_width, max_width = character_dimensions

print("Number of regions detected:", len(list(regionprops(labelled_plate))))
characters = []
counter=0
column_list = []
for regions in regionprops(labelled_plate):
    y0, x0, y1, x1 = regions.bbox
    region_height = y1 - y0
    region_width = x1 - x0

    if region_height > min_height and region_height < max_height and region_width > min_width and region_width < max_width:
        roi = license_plate[y0:y1, x0:x1]

        rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="red",
                                       linewidth=2, fill=False)
        ax1.add_patch(rect_border)
        
        resized_char = resize(roi, (20, 20))
        characters.append(resized_char)
        counter += 1
        column_list.append(x0)


plt.show()