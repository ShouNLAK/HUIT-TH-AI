import math

def giai_pt_bac_1(a, b):
    if a == 0:
        return "Vô số nghiệm" if b == 0 else "Vô nghiệm"
    return f"Nghiệm x = {-b/a}"

def giai_pt_bac_2(a, b, c):
    if a == 0:
        return giai_pt_bac_1(b, c)
    delta = b**2 - 4*a*c
    if delta < 0:
        return "Phương trình vô nghiệm"
    elif delta == 0:
        return f"Phương trình có nghiệm kép x = {-b/(2*a)}"
    else:
        x1 = (-b + math.sqrt(delta)) / (2*a)
        x2 = (-b - math.sqrt(delta)) / (2*a)
        return f"Phương trình có 2 nghiệm phân biệt: x1 = {x1}, x2 = {x2}"

if __name__ == "__main__":
    print("Giải PT Bậc 1 (2x - 4 = 0):", giai_pt_bac_1(2, -4))
    print("Giải PT Bậc 2 (x^2 - 3x + 2 = 0):", giai_pt_bac_2(1, -3, 2))
