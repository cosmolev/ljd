local function calculate(n)
  local value = n * n - 3 * n + 7
  if n < 0 then value = value + 11 elseif n == 0 then value = 19 else value = value - 5 end
  return value
end
for n = -4, 6 do print(n, calculate(n)) end
