COUNT = 0
TRACE = ""
local function event(tag)
  TRACE = TRACE .. tag
  COUNT = COUNT + 1
  return COUNT
end
local t = setmetatable({}, {
  __index = function(_, key) return event(key) end,
  __add = function() return event("+") end,
  __concat = function() return event(".") end
})
local first = t.A
local sum = t + t
print(sum, first, TRACE)
local second = t.B
local text = t .. t
print(text, second, TRACE)
local called = event("C")
local read = t.D
print(read, called, TRACE)
local read_first = t.E
local called_after = event("F")
print(called_after, read_first, TRACE)
local sum_first = t + t
print(t.G, sum_first, TRACE)
