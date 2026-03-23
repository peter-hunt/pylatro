-- Balatro-compatible RNG primitives.
-- These functions preserve operation order and numeric formatting behavior
-- from the original Lua implementation.

PylatroRNG = {}

local G = {
  GAME = {
    pseudorandom = {}
  }
}

local _compat_rand_state = 0

local function _quantize_13(v)
  local scale = 10000000000000 -- 1e13
  if v >= 0 then
    return math.floor(v * scale + 0.5) / scale
  end
  return math.ceil(v * scale - 0.5) / scale
end

local function _compat_randomseed(seed)
  local n = tonumber(seed) or 0
  if n ~= n or n == math.huge or n == -math.huge then n = 0 end
  -- Balatro seeds RNG from [0,1) values after pseudoseed; map into 31-bit domain.
  _compat_rand_state = math.floor(math.abs(n) * 2147483647) % 2147483648
end

local function _compat_random(min, max)
  _compat_rand_state = (1103515245 * _compat_rand_state + 12345) % 2147483648
  local r = _compat_rand_state / 2147483648

  if min and max then
    return math.floor(r * (max - min + 1)) + min
  end
  if min then
    return math.floor(r * min) + 1
  end
  return r
end

function PylatroRNG.pseudohash(str)
  local num = 1
  for i=#str, 1, -1 do
      num = ((1.1239285023/num)*string.byte(str, i)*math.pi + math.pi*i)%1
  end
  return num
end

function PylatroRNG.pseudoseed(key, predict_seed)
  if key == 'seed' then return _compat_random() end

  if predict_seed then
    local _pseed = PylatroRNG.pseudohash(key..(predict_seed or ''))
    _pseed = math.abs(_quantize_13((2.134453429141+_pseed*1.72431234)%1))
    return (_pseed + (PylatroRNG.pseudohash(predict_seed) or 0))/2
  end

  if not G.GAME.pseudorandom[key] then
    G.GAME.pseudorandom[key] = PylatroRNG.pseudohash(key..(G.GAME.pseudorandom.seed or ''))
  end

  G.GAME.pseudorandom[key] = math.abs(_quantize_13((2.134453429141+G.GAME.pseudorandom[key]*1.72431234)%1))
  return (G.GAME.pseudorandom[key] + (G.GAME.pseudorandom.hashed_seed or 0))/2
end

function PylatroRNG.pseudorandom(seed, min, max)
  if type(seed) == 'string' then seed = PylatroRNG.pseudoseed(seed) end
  _compat_randomseed(seed)
  if min and max then return _compat_random(min, max)
  else return _compat_random() end
end

function PylatroRNG.pseudorandom_element(_t, seed)
  if seed then _compat_randomseed(seed) end
  local keys = {}
  for k, v in pairs(_t) do
      keys[#keys+1] = {k = k, v = v}
  end

  if keys[1] and keys[1].v and type(keys[1].v) == 'table' and keys[1].v.sort_id then
    table.sort(keys, function(a, b) return a.v.sort_id < b.v.sort_id end)
  else
    table.sort(keys, function(a, b) return a.k < b.k end)
  end

  local key = keys[_compat_random(#keys)].k
  return _t[key], key
end

function PylatroRNG.pseudoshuffle(list, seed)
  if seed then _compat_randomseed(seed) end

  if list[1] and list[1].sort_id then
    table.sort(list, function(a, b) return (a.sort_id or 1) < (b.sort_id or 2) end)
  end

  for i = #list, 2, -1 do
    local j = _compat_random(i)
    list[i], list[j] = list[j], list[i]
  end
end

function PylatroRNG.init(seed)
  G.GAME.pseudorandom = {}
  G.GAME.pseudorandom.seed = seed
  G.GAME.pseudorandom.hashed_seed = PylatroRNG.pseudohash(seed)
end

function PylatroRNG.get_key_state(key)
  return G.GAME.pseudorandom[key]
end

function PylatroRNG.set_key_state(key, value)
  G.GAME.pseudorandom[key] = value
end

function PylatroRNG.snapshot_state()
  local out = {}
  for k, v in pairs(G.GAME.pseudorandom) do
    out[k] = v
  end
  return out
end

function PylatroRNG.restore_state(state)
  G.GAME.pseudorandom = {}
  for k, v in pairs(state) do
    G.GAME.pseudorandom[k] = v
  end
end

function PylatroRNG.pick_element_by_key(key, list)
  return PylatroRNG.pseudorandom_element(list, PylatroRNG.pseudoseed(key))
end

function PylatroRNG.shuffle_by_key(key, list)
  PylatroRNG.pseudoshuffle(list, PylatroRNG.pseudoseed(key))
  return list
end
