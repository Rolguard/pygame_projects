import pygame
import csv
import os


# Loads an image from the given path
def load_image(path, scale, alpha):
    if alpha:
        img = pygame.image.load(f"{path}").convert_alpha()
    else:
        img = pygame.image.load(f"{path}").convert()

    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    return img


# Loads multiple images from files in folder_path into a list
# Images must be numbered from 0, e.g. 0.png, 1.png
def load_image_list(folder_path, scale, num_images):
    images = []
    if os.path.exists(folder_path):
        for i in range(num_images):
            file_path = f"{folder_path}/{i}.png"
            img = load_image(file_path, scale, True)
            images.append(img)

    return images


# Returns list of rows (lists) containing integers which represent different tile types
# By reading csv file
def load_level(csv_file_name, local_level_data):
    with open(csv_file_name, "r", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # Reader returns many lists (rows) of strings
        for row_idx, row in enumerate(csv_reader):
            for col_idx, tile in enumerate(row):
                local_level_data[row_idx][col_idx] = int(tile)

    return local_level_data
