import os
from PIL import Image, ImageDraw
def read_annotation(annotation_path: str):
    """
    Чтение аннотаций из файла TXT.
    """
    with open(annotation_path, "r") as file:
        lines = file.readlines()
    bounding_boxes = []
    for line in lines:
        parts = line.strip().split(" ")
        class_id = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        bounding_boxes.append((class_id, x, y, w, h))
    return bounding_boxes
