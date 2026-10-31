local function make(seed)
  local value = seed
  local function add(n) value = value + n; return value end
  local function read() return value end
  return add, read
end
local add, read = make(10)
local add2, read2 = make(-4)
print(add(2), read(), add2(7), read2(), add(-5), read())
local functions = {}
for i = 1, 4 do local x = i; functions[i] = function(n) x = x + n; return x end end
for i = 1, 4 do print(functions[i](3), functions[i](i)) end
