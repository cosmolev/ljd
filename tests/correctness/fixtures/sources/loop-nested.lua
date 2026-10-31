slot0, slot1, slot2 = 101, 102, 103
local function calculate(n)
  local total = 0
  while n > 0 do
    local j = n
    repeat
      total = total + j
      j = j - 1
    until j == 0
    n = n - 1
  end
  return total
end
for n = 0, 6 do print(n, calculate(n)) end
print(slot0, slot1, slot2)
