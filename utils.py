import numpy as np
import math
import matplotlib.pyplot as plt


def is_prime(n):
    if n % 2 == 0 and n > 2:
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))


def generatePath(shs, pos, coop, player_num):
    f = open("strongholds.qs", "w+")
    print(str(len(shs)), "0", file=f)
    for sh in shs:
        print(str(sh[0]), str(sh[1]), file=f)
    f.close()
    
    while True:
        # try:
        input(
            "Use the strongholds.qs file in this directory to run concorde pathfinding, then once you solve and save, press enter"
        )

        f = open("strongholds.qs", "r")
        lines = f.readlines()
        f.close()

        paths = {}
        for i in range(len(shs) + 1, len(lines)):
            start, end, dist = lines[i].split()
            paths[int(start)] = int(end)

        rev_paths = dict((v, k) for k, v in paths.items())

        new_x, new_z = zip(*shs)

        # Have to scale numbers down due to overflow errors
        new_x = np.array(list(new_x)) / 100
        new_z = np.array(list(new_z)) / 100
        pos = (pos[0] / 100, pos[1] / 100)

        dists = np.sqrt(((new_x - pos[0]) ** 2) + ((new_z - pos[1]) ** 2))
        nearest_idx = np.argmin(dists)
        normal = get_dist(shs[nearest_idx], shs[paths[nearest_idx]])
        reverse = get_dist(shs[nearest_idx], shs[rev_paths[nearest_idx]])
        if coop and player_num == 2:
            paths = rev_paths
        elif normal > reverse:
            paths = rev_paths
        break
    # except Exception as e:
    #     print("Something went wrong, make sure you hit save, and try again")
    #     print(e)
    #     continue

    return paths, nearest_idx


def get_dist(x1, x2):
    return np.sqrt(((x1[0] - x2[0]) ** 2) + ((x1[1] - x2[1]) ** 2))


def updateCount(count):
    f = open("sh_count.txt", "w+")
    facts = open("fun_facts.txt", "w+")

    lines = [str(count) + "/128\n"]

    if count == 69:
        facts.writelines(["nice.\n"])
    if count == 71:
        facts.writelines(["BRA7-1L\n"])
    if is_prime(count):
        facts.writelines(["(prime)\n"])

    f.writelines(lines)

    f.close()
    facts.close()


def printHelp():
    print(
        "\n-------------------------------------------------------------------------------------------\n"
        "All valid commands\n"
        + "Enter\t\t-\t"
        + "Marks stronghold as complete and updates count\n"
        + "0\t\t-\t"
        + "Marks that you checked the coordinates but there was no stronghold\n"
        + "e\t\t-\t"
        + "Allows you to manually adjust the stronghold count\n"
        + "d\t\t-\t"
        + "Mark that you went back to spawn, and restart pathfinding from 0 0\n"
        + "d*\t\t-\t"
        + "Restart pathfinding from specific coordinates\n"
        + "-------------------------------------------------------------------------------------------\n"
    )


def getCoords(prompt):
    while True:
        try:
            user_input = input(prompt)
            results = parseCoords(user_input)
            if len(results) != 2:
                print(
                    "Make sure you are only typing your x and z coordinate, or are copying f3+c only"
                )
                continue
            return results
        except Exception as e:
            print(
                "Make sure you are only typing your x and z coordinate, or are copying f3+c only"
            )
            continue


def parseCoords(user_input):
    integers = user_input.split()
    if "/" == user_input[0]:
        integers = [integers[6], integers[8]]
        integers = list(map(float, integers))
    return list(map(int, integers))


def getInt(prompt):
    while True:
        try:
            user_input = input(prompt)
            integers = user_input.split()
            if len(integers > 1):
                print("Expected only one number")
                continue
            results = list(map(int, integers))
            return results
        except Exception as e:
            print("Integer only input. Just type one number and hit enter")
            continue


def graphAddSH(prev, sh, col1, flag):
    line = plt.arrow(
        prev[0],
        prev[1],
        sh[0] - prev[0],
        sh[1] - prev[1],
        color=col1,
        width=0.0001,
        head_width=0,
        head_length=0,
        length_includes_head=True,
    )
    point = None
    if not flag:
        point = plt.scatter(sh[0], sh[1], c=col1, s=30)
    plt.savefig("output.png", bbox_inches="tight", transparent=True)
    return line, point
