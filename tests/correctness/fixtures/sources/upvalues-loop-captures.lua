local numeric, iterator, while_loop, repeated = {}, {}, {}, {}
for i = 1, 3 do
  numeric[i] = function() return i end
end
for i, value in ipairs({10, 20, 30}) do
  iterator[i] = function() return i, value end
end
local n = 0
while n < 3 do
  n = n + 1
  local value = n * 10
  while_loop[n] = function(delta) value = value + delta; return value, n end
end
n = 0
repeat
  n = n + 1
  local value = n * 100
  repeated[n] = function() return value end
until n == 3
for i = 1, 3 do
  print(numeric[i]())
  print(iterator[i]())
  print(while_loop[i](1))
  print(while_loop[i](2))
  print(repeated[i]())
end
