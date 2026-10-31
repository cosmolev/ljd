local function pack(...) return select("#", ...), {...} end
local function values(x) return x, nil, x + 2 end
local function forward(...) return pack(...) end
local n, t = forward(values(5))
print(n, t[1], t[2], t[3])
local a, b, c = values(8)
print(a, b, c)
local x, y = 1, 2
x, y = y, x
print(x, y, (values(9)))
