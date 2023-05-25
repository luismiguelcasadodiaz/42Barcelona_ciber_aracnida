#!/Users/lcasado-/miniconda3/envs/42AI-lcasado-/bin/python
"""
Le deuxième programme scorpion recevra des fichiers d’images en tant que
paramètres et sera capable de les analyser pour en extraire les métadonnées
EXIF et autres, en les affichant à l’écran.

Le programme sera au moins compatible avec les mêmes extensions que celles
gérées par spider. Il affichera les attributs de base tels que la date de
création, ainsi que les données EXIF. Le format de sortie dépend de vous.


./scorpion FILE1 [FILE2 ...]
"""
import argparse
import exifread
import pprint
import sys
import os

ALLOWED_IMG_EXTE = tuple([".jpg", ".JPG", ".jpeg", ".JPEG",
                          ".png", ".PNG", ".gif", ".GIF",
                          ".bmp", ".BMP", ".pdf", ".PDF",
                          ".docx", ".DOCX"])


def options():
    parser = argparse.ArgumentParser(description="Scorpion Reads\
                                     image metadata")
    parser.add_argument("file", help="Input image file.", nargs='+')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = options()
    print(args)

    cwd = os.getcwd()

    for file in args.file:
        extension = file[file.rfind("."):]
        # print("==>",file, extension)
        if extension not in ALLOWED_IMG_EXTE:
            print(f"File format {extension} not supported")
            m = [x for idx, x in enumerate(ALLOWED_IMG_EXTE) if idx % 2 == 0]
            print(f"I am ready only for {m}")
            exit()
        scorpiopath = os.path.join(cwd, file)
        with open(scorpiopath, 'rb') as image_file:
            my_image = exifread.process_file(image_file)
            tags = my_image.keys()
            if len(tags) == 0:  # this image has not EXIF data
                print(f"No metadata in {scorpiopath}")
            else:
                print()
                print(f"Metadata  from {scorpiopath}")
                print("==============", "=" * len(scorpiopath))
                for tag in my_image.keys():
                    if tag != "JPEGThumbnail":
                        print(f"{tag}:{my_image[tag]}")
                print("==============", "=" * len(scorpiopath))
