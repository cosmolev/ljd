ljd_loop_trace = ""
function ljd_loop_take(n)
  ljd_loop_trace = ljd_loop_trace .. tostring(n) .. ":"
  return n * 2
end
local function calculate(n)
  local total = 0
  while n > 0 do
    local previous = ljd_loop_take(n)
    n = n - 1
    total = total + previous + n
  end
  return total, n
end
print(calculate(4))
print(ljd_loop_trace)
