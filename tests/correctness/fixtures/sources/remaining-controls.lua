local t = {value = 4}
function t:add(n) self.value = self.value + n; return self.value end
print(t:add(7), t.value)
local calls = 0
local function hit(x) calls = calls + 1; return x end
local function choose(a, b)
  return a and hit(b) or hit(17), not a or hit(true)
end
print(choose(false, 4)); print(calls)
print(choose(true, false)); print(calls)
print(choose(true, 8)); print(calls)
