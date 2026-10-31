local t = {4, 5}
local before = t[2]
local alias = t
alias[2] = 9
print(before, t[2])
t[1], t[2] = t[2], t[1]
print(t[1], t[2])
local function mutate(p) p[1] = 50 end
local saved = t[1]
mutate(t)
print(saved, t[1])
