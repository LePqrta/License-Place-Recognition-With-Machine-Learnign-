import os
import segmentation
import joblib
import numpy as np

def predict_license_plate(image_path):
    result = segmentation.segmentation(image_path)
    if result == "Plate Not Found":
        return result
    characters, column_list = result
    
    print(f"\nCharacters received: {len(characters)}")
    print(f"Column list: {column_list}")
    
    if len(characters) == 0:
        return "No characters detected"
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    model_dir = os.path.join(current_dir, 'models/svc/svc.pkl')
    model = joblib.load(model_dir)

    classification_result = []
    for idx, each_character in enumerate(characters):
        # Ensure the character is properly flattened
        print(f"Character {idx} shape before reshape: {each_character.shape}")
        flat_char = each_character.reshape(1, -1)
        print(f"Character {idx} shape after reshape: {flat_char.shape}")
        result = model.predict(flat_char)
        classification_result.append(result)
        print(f"Character {idx} prediction: {result[0]}")

    print(f"\nAll predictions: {classification_result}")

    plate_string = ''
    for eachPredict in classification_result:
        plate_string += eachPredict[0]

    print(f"Plate string (unsorted): {plate_string}")

    # Sort characters by their column position (left to right)
    if len(column_list) != len(plate_string):
        print(f"WARNING: column_list length ({len(column_list)}) != plate_string length ({len(plate_string)})")
        return plate_string
    
    column_list_copy = column_list[:]
    column_list.sort()
    rightplate_string = ''
    for each in column_list:
        idx = column_list_copy.index(each)
        rightplate_string += plate_string[idx]
        print(f"Sorted position: column={each} -> char='{plate_string[idx]}'")

    print(f"Plate string (sorted): {rightplate_string}")
    return rightplate_string