READS = 0
TRACE = ""
local meta = {__index = function(_, key)
  READS = READS + 1
  TRACE = TRACE .. key
  return READS
end}
local a = setmetatable({}, meta)
local b = setmetatable({}, meta)
local first = a.A
local second = b.B
print(second, first, READS, TRACE)
local third, fourth = a.C, a.D
print(fourth, third, READS, TRACE)
local saved = a.E
print(b.F, saved, READS, TRACE)

local sink = setmetatable({}, {__newindex = function(_, key, value)
  TRACE = TRACE .. key
  READS = READS + value
end})
local before = a.G
sink.H = 10
print(before, READS, TRACE)
local after = a.I
print(READS, after, TRACE)
