local function calculate(n)
  local total = 0
  while n > 0 do
    total = total + n
    if n % 3 == 0 then
      total = total + 100
      break
    end
    n = n - 1
  end
  for i = 1, 8 do
    if i > n then break end
    total = total + i
  end
  return total, n
end
for n = 0, 8 do print(n, calculate(n)) end
