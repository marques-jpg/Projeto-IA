import os
import time
import subprocess

TEST_DIR = "slitherlink-boards-public"

def executar_testes_automaticos():
    if not os.path.exists(TEST_DIR):
        print(f"Erro: A pasta '{TEST_DIR}' não foi encontrada.")
        print("Garante que estás a correr o script na raiz do projeto.")
        return

    print("=" * 65)
    print(f"{'FICHEIRO DE TESTE':<22} | {'ESTADO':<12} | {'TEMPO DE EXECUÇÃO'}")
    print("=" * 65)

    testes_passados = 0
    total_testes = 0

    ficheiros = sorted(os.listdir(TEST_DIR))
    test_files = [f for f in ficheiros if f.endswith(".txt")]

    for filename in test_files:
        total_testes += 1
        nome_base = filename[:-4]  # Remove o '.txt'
        txt_path = os.path.join(TEST_DIR, filename)
        out_path = os.path.join(TEST_DIR, nome_base + ".out")

        if not os.path.exists(out_path):
            print(f"{filename:<22} | {'SEM .OUT':<12} | ---")
            continue

        with open(out_path, 'r') as f:
            conteudo_esperado = f.read().strip().split()

        tempo_inicio = time.time()
        try:
            with open(txt_path, 'r') as input_file:
                resultado = subprocess.run(
                    ["python3", "slitherlink.py"],
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=20000
                )
            tempo_fim = time.time()
            tempo_decorrido = tempo_fim - tempo_inicio

            if resultado.returncode != 0:
                print(f"{filename:<22} | \033[91mERRO EXEC\033[0m   | {tempo_decorrido:.3f}s")
                continue

            conteudo_obtido = resultado.stdout.strip().split()

            if conteudo_obtido == conteudo_esperado:
                print(f"{filename:<22} | \033[92mPASSED\033[0m     | {tempo_decorrido:.3f}s")
                testes_passados += 1
            else:
                print(f"{filename:<22} | \033[91mFAILED\033[0m     | {tempo_decorrido:.3f}s")

        except subprocess.TimeoutExpired:
            print(f"{filename:<22} | \033[93mTIMEOUT\033[0m    | >15.000s (Demasiado Lento)")

    print("=" * 65)
    print(f"Resumo do Avaliador: {testes_passados}/{total_testes} testes bem-sucedidos.")
    print("=" * 65)

if __name__ == "__main__":
    executar_testes_automaticos()