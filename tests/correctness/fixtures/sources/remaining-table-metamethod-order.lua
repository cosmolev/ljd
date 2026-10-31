READS = 0
local meta = {__index = function()
  READS = READS + 1
  return READS
end}
local t = setmetatable({}, meta)
local first = t.missing
local second = t.missing
print(second, first, READS)
