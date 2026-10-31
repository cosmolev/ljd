local calls = 0
local function hit(x) calls = calls + 1; return x end
local function choose(a, b)
  local x = a and hit(b) or hit(17)
  local y = not a or hit(true)
  return x, y
end
print(choose(false, 4)); print(calls)
print(choose(true, false)); print(calls)
print(choose(true, 8)); print(calls)
local z = 0/0
print(z < 0, not (z < 0), z >= 0)
