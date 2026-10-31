local function calculate(n)
  local total = 0
  repeat
    total = total + n
    n = n - 1
  until n <= 0
  return total, n
end
for n = -2, 8 do print(n, calculate(n)) end
