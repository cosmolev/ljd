uv0, uv1, slot0 = 100, 200, 300
local function outer(uv0_)
  local value = 7
  local first = function() return value, uv0, uv0_, slot0 end
  do
    local value = 9
    local second = function() return value, uv1 end
    print(second())
  end
  value = 8
  return first
end
local first = outer(400)
print(first())
print(uv0, uv1, slot0)
