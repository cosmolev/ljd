local function calculate(n)
  local total = 0
  for i = 1, n do
    if i % 3 == 0 then total = total - i else total = total + i * 2 end
  end
  local j = n
  while j > 0 do total = total + j; j = j - 2 end
  repeat total = total - 1 until total % 4 == 0
  local t = {2, 5, 9, 12}
  for k, v in ipairs(t) do total = total + k * v end
  return total
end
for n = 1, 15 do print(n, calculate(n)) end
