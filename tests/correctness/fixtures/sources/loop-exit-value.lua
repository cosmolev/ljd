local function numeric(n)
  local result = -1
  for i = 1, n do result = i * 2 end
  return result
end
local function iterator(values)
  local result = -1
  for i, value in ipairs(values) do result = value * 3 end
  return result
end
for n = 0, 5 do print(n, numeric(n)) end
print(iterator({}), iterator({2}), iterator({2, 5, 9}))
