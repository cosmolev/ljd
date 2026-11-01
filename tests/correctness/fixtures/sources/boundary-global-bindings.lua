SHADOW = "global"
local function read_global() return SHADOW end
do
  local SHADOW = "block"
  print(SHADOW, read_global())
end
print(SHADOW)
local function check(SHADOW)
  print(SHADOW, read_global())
end
check("parameter")
do
  local SHADOW_2 = "reserved"
  do
    local SHADOW = "nested"
    print(SHADOW, read_global())
  end
  print(SHADOW_2)
end
local function later() return SHADOW end
print(later(), SHADOW)
