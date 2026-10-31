local a, b, set_a, set_b
do
  local value = 11
  a = function() return value end
  set_a = function(next_value) value = next_value end
end
do
  local value = 22
  b = function() return value end
  set_b = function(next_value) value = next_value end
end
print(a(), b())
set_a(30)
print(a(), b())
set_b(nil)
print(a(), b())
local value = 100
print(value, a(), b())
