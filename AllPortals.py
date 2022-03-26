import os
import numpy as np
from utils import *
import matplotlib.pyplot as plt
from Sheets import *

coop = True
players = 2
player_num = 1
name = "Mime"
shared = setup()
ws = createWorkSheet(name)

first_strongholds = []
sh_per_ring = [3, 6, 10, 15, 21, 28, 36, 10]
magnitude_per_ring = [2048, 5120, 8192, 11264, 14336, 17408, 20480, 23552]
count = 0
updateCount(count)

img = plt.imread("rings.png")
plt.imshow(img, aspect="equal", extent=[-24320, 24320, -24320, 24320])
plt.axis("off")
plt.savefig("output.png", bbox_inches="tight", transparent=True)

prev = (0, 0)
if not coop:
    for i in range(1, 9):
        sh = getCoords("Stronghold in ring " + str(i) + ":")
        count += 1
        updateCount(count)
        graphAddSH(prev, sh, "green", False)
        prev = sh
else:
    while True:
        first_strongholds = getData(0)
        if len(first_strongholds) == 8 and ["", ""] not in first_strongholds:
            print("First stronghold in each ring has been found")
            break
        user_input = input("Stronghold coords:")
        try:
            sh = parseCoords(user_input)
            magnitude = np.sqrt(sh[0] ** 2 + sh[1] ** 2)
            dists = np.abs(magnitude_per_ring - magnitude)
            row = np.argmin(dists) + 2
            sheet_range = "A" + str(row) + ":B" + str(row)
            shared.update(sheet_range, [[sh[0], sh[1]]])
            addData([sh[0], sh[1]], ws)
        except Exception as e:
            print(e)
            pass

new_strongholds = []
print(len(first_strongholds))
# Predict location of all the other strongholds
for i in range(len(first_strongholds)):
    x, z = first_strongholds[i]
    magnitude = magnitude_per_ring[i]
    vec1 = np.array([x, z])
    vec2 = np.array([1, 0])
    ang = np.arctan2(vec1[1], vec1[0]) - np.arctan2(vec2[1], vec2[0])
    for j in range(sh_per_ring[i] - 1):
        ang += (2 * np.pi) / sh_per_ring[i]
        new_x = magnitude * np.cos(ang)
        new_z = magnitude * np.sin(ang)
        new_strongholds.append((round(new_x), round(new_z)))

print(len(new_strongholds), first_strongholds)
paths, nearest_idx = generatePath(
    new_strongholds, first_strongholds[-1], coop, player_num
)

nearest = new_strongholds[nearest_idx]
eighth_ring = new_strongholds[-9:]
curr = nearest_idx


plt.scatter(*zip(*new_strongholds), c="gray", s=20)
plt.savefig("output.png", bbox_inches="tight", transparent=True)

print("\nPress enter to receive next stronghold or 'h' for alternative commands\n")

completed = first_strongholds
unfinished = new_strongholds
prev = completed[-1]
c2 = False
noGraph = False
while count < 128:
    # dist = get_dist(new_strongholds[next], new_strongholds[int(prev)])
    completed.append(prev)

    sh = unfinished[curr]
    sh_n = (round(sh[0] / 8), round(sh[1] / 8))

    line, point = graphAddSH(prev, sh, "blue", c2)
    if not noGraph:
        graphAddSH(
            completed[-2], prev, "green", c2
        )  # Do not mark sh as finished if there was a reset

    noGraph = False
    c2 = False
    prev = sh

    while True:
        prompt = "Stronghold " + str(count + 1) + ":\t" + str(sh_n) + "\n"

        if sh in eighth_ring:
            prompt += "8th ring, there could be no stronghold\n"

        user = input(prompt)

        if user == "":
            count += 1
            addData(sh_n, ws)
            break
        elif user == "h":
            printHelp()
        elif user == "0":
            c2 = True
            point.remove()
            plt.draw()
            break
        elif user == "e":
            new_count = getInt(
                "Type in the new number of strongholds you have completed\n"
            )
            count = new_count
            updateCount(count)
        elif user == "d" or user == "d*":
            pos = (0, 0)
            if user == "d*":
                pos = tuple(
                    getCoords(
                        "Type out your x and z coordinates you want to start pathfinding from (OW):\n"
                    )
                )
            unfinished = list(set(unfinished) - set(completed))
            paths, curr = generatePath(unfinished, pos)

            sh = unfinished[curr]  # Next stronghold starting from 0,0
            prev = sh
            completed.append(pos)
            # Update prompt to nether coords
            sh_n = (round(sh[0] / 8), round(sh[1] / 8))

            # Clean graph's in progress stuff
            try:
                line.remove()
                point.remove()
            except Exception as e:
                print(
                    "Must've forgotten bed after finding empty 8th ring sh, or else something went really wrong"
                )

            plt.draw()
            graphAddSH(pos, sh, "blue", c2)
    curr = paths[curr]
    updateCount(count)
