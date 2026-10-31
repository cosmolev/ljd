local function outer(value)
  local function middle(delta)
    local function inner(amount)
      value = value + delta + amount
      return value, delta
    end
    return inner
  end
  return middle, function() return value end
end
local middle, read = outer(7)
local a, b = middle(2), middle(5)
print(a(1))
print(b(3))
print(a(-2))
print(read())
