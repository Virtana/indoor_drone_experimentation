# import cv2
import os
import re
import numpy as np
import time
import cv2

def decode_image(file: str) -> np.ndarray:
    data: bytes = None
    
    with open(file, "rb") as f:
        data = f.read()
    
    pixels = []
    for i in range(1, len(data), 2):
        # print(f"{int(data[i-1])} | {int(data[i])}")
        pixel_val = int(data[i]) << 8 | int(data[i-1])
        pixel_val = int((pixel_val / 1023) * 65535)
        # print(pixel_val)
        pixels.append(pixel_val)
        # print(pixel_val)

    
    return np.array(pixels, dtype=np.uint16).reshape(720, 1280)



def extract_ts(file: str) -> int:
    ts = re.findall('\d+', file)
    if ts:
        return int(ts[0])
    else:
        print("No timestamp in image name")
        return -1


def main():
    mount_path = "./som_share/"

    while True:
        time.sleep(0.1)
        files = os.listdir(mount_path)
        files = [f for f in files if f.endswith(".raw")]

        files.sort(key=extract_ts)

        for f in files:
            print(mount_path + f)

            img = decode_image(mount_path + f)

            cv2.imshow("out", img)
            cv2.waitKey(1)

            os.remove(mount_path + f)

    return 0


if __name__=="__main__":
    main()
