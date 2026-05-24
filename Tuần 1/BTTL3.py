# Xóa khoảng trắng thừa ở đầu và cuối chuỗi “ Hello World". Chuyển hoa và thường. Thay H thành J.
s = " Hello World "
s = s.strip()
print("Xóa khoảng trắng:", s)
print("Hoa:", s.upper())
print("Thường:", s.lower())
print("Thay H thành J:", s.replace('H', 'J'))
