local function make()
  local a, b, c = 1, 2, 3
  local function read() return a, b, c end
  local function update(x, y, z) a, b, c = x, y, z end
  return read, update
end
local read, update = make()
print(select('#', read()), read())
update(4, nil, 6)
print(select('#', read()), read())
local function pair() return 10, 20 end
local first, second = pair()
local function capture() return second end
print(first, capture())
