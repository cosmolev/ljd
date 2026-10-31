local function pair(x) return x, x+1 end
local t = {name="alpha", [3]=9, pair(4)}
t.name = t.name .. "-beta"
local old = t[1]
t[1], t[2] = t[2], t[1]
print(t.name, old, t[1], t[2], t[3])
local total = 0
for k, v in pairs({a=2, b=7, c=11}) do total = total + v end
print(total)
local out = {}
for i = 1, 8 do out[i] = tostring(i * i) end
print(table.concat(out, ":"))
