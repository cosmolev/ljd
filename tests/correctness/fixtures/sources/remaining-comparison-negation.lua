local function show(x, y)
  print(x < y, not (x < y), x <= y, not (x <= y))
  print(x > y, not (x > y), x >= y, not (x >= y))
end
show(0/0, 1)
show(1, 0/0)
show(1, 2)
show(2, 1)
show(2, 2)
local meta = {
  __lt = function(a, b) print("lt", a.tag, b.tag); return false end,
  __le = function(a, b) print("le", a.tag, b.tag); return false end
}
local a = setmetatable({tag = "a"}, meta)
local b = setmetatable({tag = "b"}, meta)
print(not (a < b), a >= b)
