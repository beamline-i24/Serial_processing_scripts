

listy = []
f = open('pacman.dat', 'r')
g = open('pacman_CLEAN.dat', 'w')
for line in f.readlines():
    listy.append(line)

sety = set(listy)

print len(listy)
print len(sety)
f.close()

for x in sety:
    g.write(x)
g.close()

