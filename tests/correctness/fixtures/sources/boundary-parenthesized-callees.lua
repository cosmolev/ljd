print("before method");
({tag = "table", run = function(self, n) print(self.tag, n) end}):run(7)
print("before string");
("abc"):sub(1, 2)
print("before chain");
(function() return function(value) print(value) end end)()("chained")
local function nested()
  ({tag = "first", run = function(self) print(self.tag) end}):run()
end
nested()
