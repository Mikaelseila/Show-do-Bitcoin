import requests
import os
import json
import sys
import random



def get_token():
    response = requests.get('https://tryvia.ptr.red/api_token.php?command=request')
    # TODO: considere response_code != 0
    dados = response.json()
    return dados['token']


def get_questions(token, qtd_questions, difficulty):
    category = 0
    response = requests.get(f'https://tryvia.ptr.red/api.php'
                            f'?amount={qtd_questions}'
                            f'&category={category}'
                            f'&type=multiple'
                            f'&difficulty={difficulty}'
                            f'&token={token}')
    # TODO: considere response_code != 0

    dados = response.json()
    if dados['response_code'] != 0:
        print("erro de conexão, por favor tente novamente em outra hora.")
    return dados

def jogo():
    token = get_token()

    pontuacao = {
        "pont": 0.1,
        "acertos": 1,
        "pulos": 3
    }
    dados_easy = get_questions(token, 20, 'easy')['results']
    dados_med = get_questions(token, 20, 'medium')['results']
    dados_hard = get_questions(token, 20, 'hard')['results']

    letras = ["1", "2", "3", "4", "P", "D"]

    dif_atual = 'easy'
    pergunta_atual = dados_easy

    while True:
     for questao_alternativas in pergunta_atual:

        if pontuacao["acertos"] == 4 and dif_atual == 'easy':
            dados_easy.clear() #limpa as perguntas fáceis do banco de dados (sem o clear(), as perguntas das outras dificuldades se misturam)
            dif_atual = 'medium'
            pergunta_atual = dados_med
            continue

        if pontuacao["acertos"] == 7 and dif_atual == 'medium':
            dados_med.clear()
            dif_atual = 'hard'
            pergunta_atual = dados_hard
            continue  # próximo loop usará perguntas difíceis

        if pontuacao["acertos"] == 11 and dif_atual == 'hard':
            print("parabéns, você acabou de ganhar 1 bitcoin!")
            sys.exit()

        pontos = round(pontuacao["pont"], 1) #o round serve pra arredondar o número de bitcoins (tipo, 0.3 ao invés de 0.30000000...4, por exemplo)
        desistir_original = pontuacao["pont"] / 2
        desistir = round(desistir_original, 2)

        alternativas_juntas = questao_alternativas['incorrect_answers'] + [questao_alternativas['correct_answer']] #junta as respostas incorretas com a correta
        random.shuffle(alternativas_juntas) #embaralha todas as respostas
        while True: # caso o código não estivesse nesse while True, ele não repetiria as perguntas com uma resposta inválida ou falta de pulos.
            print( f'''\nPergunta de {pontos} BTC\n----------------------------''')  # quanto vale a pergunta de fato
            print(f'{questao_alternativas['question']}')  # mostra a questão exata
            for numero, resp in zip(letras, alternativas_juntas): #deixa elas em formato de lista
                print(f'{numero}) {resp}')

            print(f'''----------------------------\nP) pular pergunta\nD) desistir do jogo ({desistir} BTC)''') #opções de pular a pergunta ou desistir do jogo
            opcao = input("----------------------------\nescolha uma opção: ").upper()
            try:
                certo = letras.index(opcao) #converte a posição das letras da lista (linha 25) para o index delas
            except ValueError: #caso dê erro de valor (no valor "certo", por exemplo), retorna "resposta inválida".
                print("------------------------------------------\nresposta inválida, tente de novo.\n------------------------------------------")
                continue
            if opcao == "P": #pular a questão
                if pontuacao["pulos"] > 0:
                    pontuacao["pulos"] -= 1
                    print(f"------------------------------------------\npergunta pulada, resta apenas {pontuacao["pulos"]}.\n------------------------------------------") #se o jogador pular, subtrai 1 pulo do dicionário no def jogo.
                    break
                print("------------------------------------------\nvocê gastou todos os seus pulos.\n------------------------------------------")
                continue
            if opcao == "D": #desistir do jogo
                print(f"-------------------------------------------------\nvocê desistiu, e receberá o valor de {desistir} bitcoin.\n-------------------------------------------------")
                sys.exit()
            if alternativas_juntas[certo] == questao_alternativas['correct_answer']: #se a pergunta estiver correta, adiciona a pontuação e a quantidade de acertos
                print("------------------------------------------\ncerta resposta!\n------------------------------------------")
                pontuacao["pont"] += 0.1
                pontuacao["acertos"] +=1
                break
            else: #caso erre a pergunta, o jogo acaba.
              print("------------------------------------------\nNÃO!")
              print("------------------------------------------\na resposta certa era: " f"{questao_alternativas['correct_answer']}")
              pontuacao_erro = pontuacao["pont"] * 0.10
              final_erro = round(pontuacao_erro, 2)
              print(f"você ganhou {final_erro} bitcoin.\n------------------------------------------")
              sys.exit()
        # print(dados['results'][0])
    return


jogo()