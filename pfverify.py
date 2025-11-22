from pfcore import generateRandomBytes, generateDouble, nextPositiveInt32

# Dice event: returns float in range [0, 100.00]
def verifyDiceEvent(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int) -> float:
    rb = generateRandomBytes(serverSeed, clientSeed, nonce, cursor)
    value = nextPositiveInt32(rb, 10001)
    return value / 100.0

# Plinko: returns bucket index (rows: 8..16, so buckets: rows+1)
def verifyPlinkoEvent(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int, rows: int) -> int:
    rb = generateRandomBytes(serverSeed, clientSeed, nonce, cursor)
    maxTraj = 2**rows
    traj = nextPositiveInt32(rb, maxTraj)
    bucketIdx = bin(traj).count('1')
    return bucketIdx

# Mines: returns a list of board tiles ("mine" or "gem")
def verifyMinesEvent(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int, edgeSize: int, numberOfMines: int) -> list:
    totalTiles = edgeSize * edgeSize
    minesPos = set()
    c = cursor
    while len(minesPos) < numberOfMines:
        rb = generateRandomBytes(serverSeed, clientSeed, nonce, c)
        pos = nextPositiveInt32(rb, totalTiles)
        if pos not in minesPos:
            minesPos.add(pos)
        c += 1
    board = []
    for idx in range(totalTiles):
        board.append('mine' if idx in minesPos else 'gem')
    return board

# Limbo: returns truncated multiplier value (usually 2 decimal places)
def verifyLimboEvent(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int, rtp: float, decimalPlaces: int=2) -> float:
    rb = generateRandomBytes(serverSeed, clientSeed, nonce, cursor)
    randFloat = generateDouble(rb)
    houseEdge = 2.0 - rtp
    multiplier = 1.0 / ((1.0 - randFloat) * houseEdge)
    # Truncate, not round
    factor = 10**decimalPlaces
    return int(multiplier * factor) / factor

# Keno: returns the set of drawn unique, nonzero numbers
def verifyKenoEvent(serverSeed: bytes, clientSeed: str, nonce: int, cursor: int, boardSize: int, drawCount: int) -> list:
    numbersDrawn = set()
    c = cursor
    while len(numbersDrawn) < drawCount:
        rb = generateRandomBytes(serverSeed, clientSeed, nonce, c)
        val = nextPositiveInt32(rb, boardSize + 1)
        if val == 0 or val in numbersDrawn:
            c += 1
            continue
        numbersDrawn.add(val)
        c += 1
    return list(numbersDrawn)
