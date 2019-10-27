x = 10


def x_globally_change():
      global x
      x = "x didn't work"
# abcd

x_globally_change()
print(x)


y = 10


def y_globally_change():
      y = "y didn't work"


y_globally_change()
print(y)
