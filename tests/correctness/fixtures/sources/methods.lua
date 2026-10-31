local Counter = {}
Counter.__index = Counter
function Counter:new(n) return setmetatable({value=n}, self) end
function Counter:add(n) self.value = self.value + n; return self.value end
function Counter:read() return self.value end
local a, b = Counter:new(4), Counter:new(20)
print(a:add(7), b:add(-2), a:read(), b:read())
local function wrap(f) return function(x) return f(x) + 1 end end
print(wrap(function(x) return x * 3 end)(9))
