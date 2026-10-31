local function calculate(n)
  local total = 0
  repeat
    local previous = n * 2
    n = n - 1
    total = total + previous + n
  until n <= 0
  return total, n
end
for n = 1, 8 do print(n, calculate(n)) end
