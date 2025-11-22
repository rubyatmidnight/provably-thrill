from pfcore import generateRandomBytes, generateDouble, nextPositiveInt32
from pfverify import verifyDiceEvent, verifyPlinkoEvent, verifyMinesEvent, verifyLimboEvent, verifyKenoEvent

# Example seeds/nonce/cursor (normally these would be secure/generated)
serverSeed = b"bKIUHib24XgY0rpaFgrrCRWHUsPetfInSWhP4xrw0aT16itCJUVqxEUSMbqe8Voc"
clientSeed = "aSoHGY9mkQqHMIcF"
nonce = 42
cursor = 0

print("Dice:", verifyDiceEvent(serverSeed, clientSeed, nonce, cursor))
print("Plinko:", verifyPlinkoEvent(serverSeed, clientSeed, nonce, cursor, rows=8))
print("Mines:", verifyMinesEvent(serverSeed, clientSeed, nonce, cursor, edgeSize=3, numberOfMines=2))
print("Limbo:", verifyLimboEvent(serverSeed, clientSeed, nonce, cursor, rtp=0.99))
print("Keno:", verifyKenoEvent(serverSeed, clientSeed, nonce, cursor, boardSize=10, drawCount=4))
