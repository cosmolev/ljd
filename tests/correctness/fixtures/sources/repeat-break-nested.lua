local total = 0
for outer = 1, 4 do
  local n = 0
  repeat
    n = n + 1
    if n == outer then break end
  until n > 8
  total = total + n
end
local outer = 0
repeat
  outer = outer + 1
  local n = 0
  repeat
    n = n + 1
    if n == 2 then break end
  until n >= 4
  total = total + outer * n
until outer == 3
print(total, outer)
