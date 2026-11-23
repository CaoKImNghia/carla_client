import carla

print("Dang ket noi CARLA...")

client = carla.Client("127.0.0.1", 2000)
client.set_timeout(10.0)

world = client.get_world()

print("Ket noi thanh cong!")
print("Map hien tai:", world.get_map().name)