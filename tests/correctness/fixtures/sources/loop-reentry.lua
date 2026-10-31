function ljd_loop_reentrant(n)
  if n == 0 then return 1 end
  local total = 0
  for i = 1, 2 do
    total = total + i * ljd_loop_reentrant(n - 1)
  end
  return total
end
for n = 0, 5 do print(n, ljd_loop_reentrant(n)) end
