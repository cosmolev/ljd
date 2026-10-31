local function values() return 9, nil, 11 end
local function count(...) print(select("#", ...), ...) end
count((values()))
count(values())
local function one() return (values()) end
count(one())
local t = {(values())}
print(t[1], t[2], t[3])
