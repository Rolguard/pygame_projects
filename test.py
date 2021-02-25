y_coordinate = 50
y_velocity = 0

for event in range(50):
    if y_coordinate > 305:
        y_velocity = -y_velocity
        print(y_velocity)

    else:
        y_velocity += 0.5
        print(y_velocity)
        print(y_coordinate)

    y_coordinate += y_velocity

