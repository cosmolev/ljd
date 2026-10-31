local outer = {tag = "outer"}
do
  local outer = {}
  outer.self = outer
  outer[outer] = "key"
  print(outer.self == outer, outer[outer])
end
print(outer.tag)
local class = {}
class.__index = class
class.value = 7
local object = setmetatable({}, class)
print(object.value, getmetatable(object) == class)
GLOBAL_SELF = {}
GLOBAL_SELF.self = GLOBAL_SELF
print(GLOBAL_SELF.self == GLOBAL_SELF)
