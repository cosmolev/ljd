local function counter(value)
  local function read() return value end
  local function write(next_value) value = next_value end
  local function add(amount) value = value + amount; return value end
  value = value + 1
  return read, write, add
end
local read, write, add = counter(6)
print(read(), add(3), read())
write(false)
print(read())
write(nil)
print(read())
write(20)
print(add(-2), read())
local other = counter(100)
print(read(), other())
