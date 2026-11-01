local t = {1}
local saved = t[1];
(function(p) p[1] = 7 end)(t)
print(saved, t[1]);
(function() print("one") end)();
(function() print("two") end)()

local function first_statement()
  (function() print("first") end)()
end
first_statement()
if t[1] == 7 then
  t[1] = 8;
  (function(p) print("nested", p[1]) end)(t)
end
repeat
  t[1] = t[1] - 1;
  (function(p) print("repeat", p[1]) end)(t)
until t[1] == 6
