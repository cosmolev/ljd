local function calculate(n)
  local total = 0
  while n > 0 do
    total = total + n
    if total > 12 then break end
    n = n - 1
  end
  repeat
    total = total + 1
    if total % 3 == 0 then break end
  until total > 30
  for i = 1, 8 do
    if i > n then break end
    total = total + i
  end
  return total, n
end
for n = 0, 8 do print(n, calculate(n)) end
