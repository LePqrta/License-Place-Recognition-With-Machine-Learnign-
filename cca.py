

from skimage import measure
from skimage.measure import regionprops
import grayscale 

def cca(image_path):

    gray_car_image, binary_car_image = grayscale.process_image(image_path)
    label_image = measure.label(binary_car_image)
    plate_dimensions=(0.08*label_image.shape[0], 0.2*label_image.shape[0],
                    0.15*label_image.shape[1], 0.4*label_image.shape[1])
    min_height, max_height, min_width, max_width = plate_dimensions

    plate_objects_cordinates = []
    plate_like_objects = []

    for region in regionprops(label_image):
        if region.area < 50:
            continue

        minRow, minCol, maxRow, maxCol = region.bbox
        region_height = maxRow - minRow
        region_width = maxCol - minCol
        if(region_height >= min_height and region_height <= max_height and
        region_width >= min_width and region_width <= max_width):
            plate_like_objects.append(gray_car_image[minRow:maxRow,
                                                                minCol:maxCol])
            plate_objects_cordinates.append((minRow, minCol, maxRow, maxCol))

    return plate_like_objects, plate_objects_cordinates

