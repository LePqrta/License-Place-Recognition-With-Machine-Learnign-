from skimage.io import imread
from skimage.filters import threshold_otsu


SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')

def process_image(image_path):
    if not image_path.lower().endswith(SUPPORTED_EXTENSIONS):
        print(f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}")
        return
    
    car_image = imread(image_path, as_gray=True)
    print(car_image.shape)

    gray_car_image = car_image * 255
    threshold_value = threshold_otsu(gray_car_image)
    binary_car_image = gray_car_image > threshold_value
    return gray_car_image, binary_car_image