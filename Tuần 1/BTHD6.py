# Tạo một list trái cây (bằng tiếng anh) fruits. Tạo một list mới chỉ chứa các loại trái cây có "a".
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
new_fruits = [f for f in fruits if "a" in f]

print("Fruits:", fruits)
print("Fruits with 'a':", new_fruits)
