local value = 4
local function change() value = value + 10; return value end
local function check()
  local before = value
  local changed = change()
  return before, changed, value
end
print(value, change(), value)
print(check())
print(check())
local function between()
  local before = change()
  change()
  return before
end
print(between(), value)
