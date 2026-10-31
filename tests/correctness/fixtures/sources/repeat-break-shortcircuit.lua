repeat_break_trace = ""
function repeat_break_first(n, limit)
  repeat_break_trace = repeat_break_trace .. "a" .. n .. ":"
  return n >= limit
end
function repeat_break_second(n)
  repeat_break_trace = repeat_break_trace .. "b" .. n .. ":"
  return n % 2 == 0
end
local function count_and(stop, limit)
  local n = 0
  repeat_break_trace = ""
  repeat
    n = n + 1
    if n == stop then break end
  until repeat_break_first(n, limit) and repeat_break_second(n)
  return n, repeat_break_trace
end
local function count_or(stop, limit)
  local n = 0
  repeat_break_trace = ""
  repeat
    n = n + 1
    if n == stop then break end
  until repeat_break_first(n, limit) or repeat_break_second(n)
  return n, repeat_break_trace
end
print(count_and(1, 3))
print(count_and(3, 3))
print(count_and(9, 3))
print(count_or(1, 3))
print(count_or(9, 3))
