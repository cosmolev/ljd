local __ljd_snapshot_2 = 99
local x, y, z = 1, 2, 3
x, y, z = y, z, x
print(x, y, z, __ljd_snapshot_2)
x, y = y, x
x, y = y, x
print(x, y, z)
local function swap(a, b)
  a, b = b, a
  return a, b
end
print(swap(4, 5))
