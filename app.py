from flask import Flask, render_template_string, request
from pfverify import (
    verifyDiceEvent,
    verifyPlinkoEvent,
    verifyMinesEvent,
    verifyLimboEvent,
    verifyKenoEvent
)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Provably Fair Verifier</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 460px; margin: auto; padding: 2em 1em; background: #f7f7f9; }
        h2 { text-align: center; }
        .frm, .res { margin: 1em 0 2em; padding: 1em; background: #fff; border-radius: 8px; border: 1px solid #ddd; }
        label { display: block; margin: 0.5em 0 0.2em; }
        select, input { margin-bottom:1em; width: 100%; font-size: 1em; padding: 0.25em; border-radius: 4px; border: 1px solid #bbb; }
        button { background:#4ADF84; color:#fff; border:none; padding:0.7em; border-radius:4px; cursor:pointer; font-size:1em; }
    </style>
</head>
<body>
    <h2>Provably Fair Verifier</h2>
    <form class="frm" method="post">
        <label>Game Type:</label>
        <select name="gameType">
            <option value="dice" {% if gameType=='dice' %}selected{% endif %}>Dice</option>
            <option value="plinko" {% if gameType=='plinko' %}selected{% endif %}>Plinko</option>
            <option value="mines" {% if gameType=='mines' %}selected{% endif %}>Mines</option>
            <option value="limbo" {% if gameType=='limbo' %}selected{% endif %}>Limbo</option>
            <option value="keno" {% if gameType=='keno' %}selected{% endif %}>Keno</option>
        </select>
        <label>Server Seed (hex or utf-8):</label>
        <input type="text" name="serverSeed" value="{{ serverSeed }}">
        <label>Client Seed:</label>
        <input type="text" name="clientSeed" value="{{ clientSeed }}">
        <label>Nonce:</label>
        <input type="number" name="nonce" value="{{ nonce }}">
        <label>Cursor:</label>
        <input type="number" name="cursor" value="{{ cursor }}">
        <label>Extra (rows/edge/mines/rtp/draw):</label>
        <input type="text" name="extra" value="{{ extra }}">
        <button type="submit">Verify!</button>
    </form>
    {% if result is defined %}
      <div class="res">
        <strong>Result:</strong>
        <pre>{{ result }}</pre>
      </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    # Retain all inputs for sticky form
    seed_data = {
        "gameType": request.form.get("gameType", "dice"),
        "serverSeed": request.form.get("serverSeed", "example_server_seed_32_bytes!!!"),
        "clientSeed": request.form.get("clientSeed", "example_client_seed"),
        "nonce": request.form.get("nonce", "42"),
        "cursor": request.form.get("cursor", "0"),
        "extra": request.form.get("extra", ""),
    }
    result = None
    if request.method == 'POST':
        game = seed_data["gameType"]
        serverSeed_raw = seed_data["serverSeed"]
        clientSeed = seed_data["clientSeed"]
        try:
            nonce = int(seed_data["nonce"])
        except Exception:
            nonce = 0
        try:
            cursor = int(seed_data["cursor"])
        except Exception:
            cursor = 0
        extra = seed_data["extra"]

        try:
            # handle seed: if hex, convert, else utf-8
            if len(serverSeed_raw) == 64 and all(c in '0123456789abcdefABCDEF' for c in serverSeed_raw):
                serverSeed = bytes.fromhex(serverSeed_raw)
            else:
                serverSeed = serverSeed_raw.encode()
        except Exception:
            result = 'Invalid serverSeed!'
            return render_template_string(HTML, result=result, **seed_data)

        try:
            if game == 'dice':
                result = verifyDiceEvent(serverSeed, clientSeed, nonce, cursor)
            elif game == 'plinko':
                rows = int(extra) if extra.isdigit() else 8
                result = verifyPlinkoEvent(serverSeed, clientSeed, nonce, cursor, rows)
            elif game == 'mines':
                parts = extra.split(',')
                edge = int(parts[0]) if len(parts)>0 and parts[0].isdigit() else 3
                mines = int(parts[1]) if len(parts)>1 and parts[1].isdigit() else 2
                result = verifyMinesEvent(serverSeed, clientSeed, nonce, cursor, edge, mines)
            elif game == 'limbo':
                rtp = float(extra) if extra else 0.99
                result = verifyLimboEvent(serverSeed, clientSeed, nonce, cursor, rtp)
            elif game == 'keno':
                parts = extra.split(',')
                board = int(parts[0]) if len(parts)>0 and parts[0].isdigit() else 10
                count = int(parts[1]) if len(parts)>1 and parts[1].isdigit() else 4
                result = verifyKenoEvent(serverSeed, clientSeed, nonce, cursor, board, count)
        except Exception as ex:
            result = f'Error: {ex}'
    return render_template_string(HTML, result=result, **seed_data)

@app.route('/pfdebug', methods=['GET', 'POST'])
def pfcore_debug():
    seed_data = {
        "serverSeed": request.form.get("serverSeed", "example_server_seed_32_bytes!!!"),
        "clientSeed": request.form.get("clientSeed", "example_client_seed"),
        "nonce": request.form.get("nonce", "0"),
        "cursor": request.form.get("cursor", "0"),
    }
    debug_out = ""
    try:
        raw_seed = seed_data["serverSeed"]
        if len(raw_seed) == 64 and all(c in '0123456789abcdefABCDEF' for c in raw_seed):
            serverSeed = bytes.fromhex(raw_seed)
        else:
            serverSeed = raw_seed.encode()
        clientSeed = seed_data["clientSeed"]
        nonce = int(seed_data["nonce"])
        cursor = int(seed_data["cursor"])
        from pfcore import generateRandomBytes, generateDouble
        import binascii
        debug_out += "PFcore Step-by-Step Debug:\n\n"
        for n in range(nonce, nonce+5):
            raw_bytes = generateRandomBytes(serverSeed, clientSeed, n, cursor, 64)
            digest_hex = binascii.hexlify(raw_bytes).decode()
            double_bytes = raw_bytes[:7]
            double_bytes_hex = binascii.hexlify(double_bytes).decode()
            bits = int.from_bytes(double_bytes, 'big')
            mantissa = bits & ((1 << 52) - 1)
            uniform = mantissa / float(1 << 52)
            scaled = uniform * 100
            debug_out += f"Nonce={n}\n"
            debug_out += f"  HMAC Digest (hex):    {digest_hex}\n"
            debug_out += f"  Double Bytes (hex):   {double_bytes_hex}\n"
            debug_out += f"  Bits:                 {bits}\n"
            debug_out += f"  Mantissa (52 bits):   {mantissa}\n"
            debug_out += f"  Uniform [0,1):        {uniform}\n"
            debug_out += f"  Scaled [0,100):       {scaled:.8f}\n\n"
    except Exception as ex:
        debug_out += f"Error: {ex}\n"
    return render_template_string("""
    <h2>PFcore Debug</h2>
    <form method="post">
      <label>Server Seed:</label><input name="serverSeed" value="{{serverSeed}}"><br>
      <label>Client Seed:</label><input name="clientSeed" value="{{clientSeed}}"><br>
      <label>Nonce (start):</label><input type="number" name="nonce" value="{{nonce}}"><br>
      <label>Cursor:</label><input type="number" name="cursor" value="{{cursor}}"><br>
      <button type="submit">Debug!</button>
    </form>
    <pre>{{debug_out}}</pre>
    """, debug_out=debug_out, **seed_data)

if __name__ == '__main__':
    app.run(debug=True)
