import prediction

# Test with a sample image
image_path = "car6.jpg"  # Replace with actual image

try:
    result = prediction.predict_license_plate(image_path)
    print(f"\nFinal Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
