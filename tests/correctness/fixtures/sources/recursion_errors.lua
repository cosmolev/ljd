local function fib(n)
  if n < 2 then return n end
  return fib(n - 1) + fib(n - 2)
end
local function check(n)
  if n < 0 then error("negative", 0) end
  return n * 2, n * 3
end
for n = 0, 9 do print(fib(n)) end
local ok, x, y = pcall(check, 4)
print(ok, x, y)
local failed, message = pcall(check, -1)
print(failed, message)
