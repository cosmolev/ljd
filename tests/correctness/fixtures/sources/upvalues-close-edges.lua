local function choose(mode)
  local result
  for i = 1, 4 do
    local value = i * 10
    result = function(delta) value = value + delta; return value, i end
    if i == mode then break end
    if mode == 0 then return result end
    value = value + 1
  end
  local value = 999
  return result, value
end
for mode = 0, 5 do
  local read, extra = choose(mode)
  print(mode, extra)
  print(read(2))
  print(read(3))
end
