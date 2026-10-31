local function factorial(n)
  if n < 2 then return 1 end
  return n * factorial(n - 1)
end
local even, odd
even = function(n)
  if n == 0 then return true end
  return odd(n - 1)
end
odd = function(n)
  if n == 0 then return false end
  return even(n - 1)
end
for i = 0, 7 do print(i, factorial(i), even(i), odd(i)) end
