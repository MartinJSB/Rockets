from os import remove
from PIL import Image

files = ['rocket_idle_green.png', 'rocket_idle_red.png', 'rocket_idle_blue.png', 'rocket_idle_yellow.png',
 'rocket_thrust_green.png', 'rocket_thrust_red.png', 'rocket_thrust_blue.png', 'rocket_thrust_yellow.png']
def removeWhites(input):
    img = Image.open(input)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(input, "PNG")

for elem in files:
    removeWhites(elem)
