# Viết chương trình in ra các cặp số (0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (3,3)
for i in range(4):
    for j in range(i + 1):
        print(f"({i},{j})", end=", " if not (i == 3 and j == 3) else "")
print()
