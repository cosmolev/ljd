local function calculate(n)
  local total = 0
  for i = 1, n do
    if i % 2 == 0 then total = total - i else total = total + i * 3 end
  end
  for i = n, 1, -2 do total = total + i end
  return total
end
for n = -1, 8 do print(n, calculate(n)) end
