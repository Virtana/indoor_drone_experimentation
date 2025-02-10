import os
import ffmpeg

source_input_dir = './Output/2025_02_07_15_20_59/mav0/cam0/data/'
source_output_dir = source_input_dir[0:-1] + '_pngs'
if not os.path.exists(source_output_dir):
    os.mkdir(source_output_dir)

for input_filename in os.listdir(source_input_dir):

    # print(input_filename)
    # # Little Endian check
    # with open(source_input_dir + input_filename, 'rb') as file:
    #     data = file.read(10)
    # for el in data:
    #     print(int(el))

    output_filename = f'{input_filename.split('_')[0]}.png'

    # Input file and parameters
    width = 1280
    height = 720
    pixel_format = "gray10le"

    # Construct the FFmpeg command
    (
        ffmpeg
        .input(source_input_dir + input_filename, format='image2', pix_fmt=pixel_format, s=f'{width}x{height}')
        .output(source_output_dir + '/' + output_filename)
        .overwrite_output()
        .run()
    )