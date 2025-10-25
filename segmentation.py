import numpy as np
from skimage.transform import resize
from skimage.filters import threshold_otsu
from skimage import measure
from skimage.measure import regionprops
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import cca

def select_plate(plate_like_objects):

    best_candidate = None
    best_score = -1
    best_regions = None
    best_char_dims = None
    
    print(f"\nAnalyzing {len(plate_like_objects)} plate-like objects:")
    
    for idx, candidate in enumerate(plate_like_objects):
        h, w = candidate.shape
        aspect_ratio = w / h
        
        thresh = threshold_otsu(candidate)
        binary_plate = candidate > thresh
        license_plate = np.logical_not(binary_plate)
        labelled_plate = measure.label(license_plate)
        regions = list(regionprops(labelled_plate))
        region_count = len(regions)
        
        print(f"\n  Object {idx}: h={h}, w={w}, aspect_ratio={aspect_ratio:.2f}, regions={region_count}")
        
        # Calculate character-like region count
        char_height_min = 0.35 * h
        char_height_max = 0.60 * h
        char_width_min = 0.05 * w
        char_width_max = 0.15 * w
        
        char_count = 0
        for region in regions:
            y0, x0, y1, x1 = region.bbox
            region_h = y1 - y0
            region_w = x1 - x0
            if char_height_min <= region_h <= char_height_max and char_width_min <= region_w <= char_width_max:
                char_count += 1
        
        # Scoring heuristics:
        score = 0
        
        # 1. License plates are typically wider than tall (aspect ratio 2-5)
        if 2.0 <= aspect_ratio <= 5.0:
            score += 10
            print(f"    ✓ Good aspect ratio: {aspect_ratio:.2f}")
        else:
            print(f"    ✗ Bad aspect ratio: {aspect_ratio:.2f} (expected 2-5)")
        
        # 2. Should have region count between 4-10
        if 4 <= region_count <= 10:
            score += 5
            print(f"    ✓ Good region count: {region_count}")
        else:
            print(f"    ✗ Bad region count: {region_count} (expected 4-10)")
        
        # 3. Should have character-like regions (at least 4)
        if char_count >= 4:
            score += (char_count * 2)  # Higher weight for more character-like regions
            print(f"    ✓ Character-like regions: {char_count}")
        else:
            print(f"    ✗ Few character-like regions: {char_count} (expected 4+)")
        
        print(f"    Score: {score}")
        
        if score > best_score:
            best_score = score
            best_candidate = candidate
            best_regions = regions
            character_dimensions = (char_height_min, char_height_max, char_width_min, char_width_max)
            best_char_dims = character_dimensions
    
    if best_candidate is not None and best_score > 0:
        print(f"\n✓ Selected object with score {best_score}")
        return best_candidate, best_regions, best_char_dims
    
    return "Plate Not Found"
def segmentation(image_path):
    plate_like_objects, plate_objects_cordinates = cca.cca(image_path)
    result = select_plate(plate_like_objects)
    if result == "Plate Not Found":
        return result
    
    gray_plate, char_regions, character_dimensions = result
    
    # CRITICAL: Invert the plate image to get white characters on black background
    thresh = threshold_otsu(gray_plate)
    binary_plate = gray_plate > thresh
    license_plate = np.logical_not(binary_plate)  # INVERT for correct character extraction
    
    min_height, max_height, min_width, max_width = character_dimensions
    
    print("Character dimension thresholds:")
    print(f"  Height: {min_height:.2f} < h < {max_height:.2f}")
    print(f"  Width: {min_width:.2f} < w < {max_width:.2f}")

    print("Number of regions detected:", len(list(char_regions)))
    characters = []
    column_list = []

    fig, ax1 = plt.subplots(1, figsize=(12, 4))
    ax1.imshow(license_plate, cmap="gray")
    ax1.set_title("Detected Character Regions")

    for regions in char_regions:
        y0, x0, y1, x1 = regions.bbox
        region_height = y1 - y0
        region_width = x1 - x0
        
        # Debug: print region dimensions
        print(f"Region: height={region_height:.2f}, width={region_width:.2f}")

        if min_height < region_height < max_height and min_width < region_width < max_width:
            roi = license_plate[y0:y1, x0:x1]  # Extract from INVERTED image
            # Draw accepted rectangle in GREEN
            rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="green",
                                           linewidth=2, fill=False)
            ax1.add_patch(rect_border)
            resized_char = resize(roi, (20, 20))
            characters.append(resized_char)
            column_list.append(x0)
            print(f"  ✓ Accepted")
        else:
            # Draw rejected rectangle in RED
            rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="red",
                                           linewidth=2, fill=False, linestyle="--")
            ax1.add_patch(rect_border)
            print(f"  ✗ Rejected")
    
    plt.tight_layout()
    plt.show()
    
    # DEBUG: Show extracted characters
    if len(characters) > 0:
        fig_chars, axes = plt.subplots(1, len(characters), figsize=(3*len(characters), 3))
        if len(characters) == 1:
            axes = [axes]
        for idx, char in enumerate(characters):
            axes[idx].imshow(char, cmap="gray")
            axes[idx].set_title(f"Char {idx}\nCol: {column_list[idx]}")
            axes[idx].axis('off')
        plt.tight_layout()
        plt.show()
    
    print("Characters extracted:", len(characters))
    print("Column list:", column_list)
    return characters, column_list
