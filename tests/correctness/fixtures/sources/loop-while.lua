local function calculate(n)
  local total = 0
  while n > 0 do
    total = total + n
    n = n - 1
  end
  return total, n
end
for n = 0, 8 do print(n, calculate(n)) end
