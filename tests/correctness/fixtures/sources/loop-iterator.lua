local function calculate()
  local total, count = 0, 0
  for k, v in pairs({a = 2, b = 7, c = 11}) do
    total = total + v
    count = count + 1
  end
  for i, v in ipairs({3, 5, 9}) do total = total + i * v end
  for i, v in ipairs({}) do total = total + v end
  return total, count
end
print(calculate())
print(calculate())
