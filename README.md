# Hologram_Photo_Albulm_Generator
A python tool to convert a directory of images to a video stream to be displayed on a custom sized pyramid projector.

The video writing relies on openCV and FFMPEG codecs. 

To use the tool call:
hologram_vid_gen.py <image_directory> <screen_diagonal_length> <pyramid_side_length> <screen_res_height> <screen_width_height> <alignment>
  
image_directory is the directory of images you wish to turn into a photo album

screen_diagonal_length is measured in inches.

pyramid_side_length is the length of a side of the smaller base of the pyramid also measured in inches.

screen_res_height is the vertical resolution of the screen you wish to display on

screen_res_width is the horizontal resolution of the screen you wish to display on

alignment will center your image on the bottom of the pyramid if specified as 'B'.
