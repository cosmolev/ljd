local function count(stop, limit)
  local n = 0
  repeat
    n = n + 1
    if n == stop then break end
  until n >= limit
  return n
end
print(count(3, 5), count(5, 3), count(1, 1), count(9, 4))
