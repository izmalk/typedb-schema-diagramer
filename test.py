
count = 0


def label():
    global count
    count += 1
    return str(count)


for i in range(5):
    print(label())

