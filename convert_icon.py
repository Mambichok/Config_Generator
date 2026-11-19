from PIL import Image

img = Image.open("resources/icon.jpg")
img = img.resize((256, 256), Image.Resampling.LANCZOS)

# Создаём иконку с несколькими размерами
sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
img.save("resources/icon.ico", format='ICO', sizes=sizes)
print("Icon created!")