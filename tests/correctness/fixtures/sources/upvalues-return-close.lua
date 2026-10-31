local function make(value)
  local function middle()
    local function last() value = value + 1; return value end
    return last
  end
  return middle
end
local a = make(7)
local b = make(20)
local a1, a2, b1 = a(), a(), b()
print(a1(), a2(), b1())
print(a1(), a2(), b1())
