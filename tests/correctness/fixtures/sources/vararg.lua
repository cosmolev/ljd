local function count(...) print(select("#", ...), ...) end
local function one(...) return (...) end
local function probe(...)
  count((...))
  count(...)
  local t = {(...)}
  print(t[1], t[2], t[3])
end
probe(9, nil, 11)
count(one(9, nil, 11))
