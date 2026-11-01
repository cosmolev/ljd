local value = "outer"
local value_2 = "reserved"
do
  local value = "inner"
  print(value)
end
print(value, value_2)
do
  local value = "sibling"
  do
    local value = value .. "-nested"
    print(value)
  end
  print(value)
end
print(value)

local function check(value)
  local before = value
  do
    local value = "parameter-shadow"
    print(value)
  end
  print(value, before)
  for value = 1, 2 do print(value) end
  print(value)
end
check("argument")
