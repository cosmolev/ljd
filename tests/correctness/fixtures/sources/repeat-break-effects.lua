repeat_break_checks = 0
function repeat_break_done(n, limit)
  repeat_break_checks = repeat_break_checks + 1
  return n >= limit
end
local function count(stop, limit)
  local n = 0
  repeat_break_checks = 0
  repeat
    n = n + 1
    if n == stop then break end
  until repeat_break_done(n, limit)
  return n, repeat_break_checks
end
print(count(1, 5))
print(count(3, 5))
print(count(5, 3))
print(count(9, 4))
