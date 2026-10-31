local bit = require("bit")
local value = 0x123456789abcdefLL
print(tostring(value), tostring(value+7LL))
print(bit.bxor(0x12345,0x78),bit.rol(17,3))
