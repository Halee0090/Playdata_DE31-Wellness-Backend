# /app/utils/image_processing.py
from PIL import Image, ExifTags
from io import BytesIO

def extract_exif_data(file_bytes: bytes):
    try:
        img = Image.open(BytesIO(file_bytes))
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag, value in exif_data.items():
            if ExifTags.TAGS.get(tag, tag) == "DateTimeOriginal":
                return value  # '2022:03:15 10:20:35'
        return None
    except Exception as e:
        raise Exception(f"Error extracting Exif data: {str(e)}")

def determine_meal_type(taken_time: str) -> str:
    try:
        time_format = "%Y:%m:%d %H:%M:%S"
        taken_time_obj = datetime.strptime(taken_time, time_format)
        hour = taken_time_obj.hour
        if 6 <= hour <= 8:
            return "아침"
        elif 11 <= hour <= 13:
            return "점심"
        elif 17 <= hour <= 19:
            return "저녁"
        else:
            return "기타"
    except Exception as e:
        raise Exception(f"Error determining meal type: {str(e)}")
