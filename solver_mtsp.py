import random as rnd
import os
import time
import math

# Função que lê os dados do arquivo da instância
def le_dados_instancia(arq_instancia):
    with open(arq_instancia, 'r') as f:
        linhas_arq = f.readlines()
        del(linhas_arq[:1])

        # Pega a quantidade de vendedores
        qtd_vendedor = int(linhas_arq[0].strip().split(';')[-1])
        del(linhas_arq[:1])
        
        mat_dist = list()
        coordenadas = list()
        # Processa todas as linhas
        for linha in linhas_arq:
            valores_linha = linha.strip().split(';')
            coord_x = int(valores_linha[0])
            coord_y = int(valores_linha[1])
            coordenadas.append((coord_x, coord_y))

            del(valores_linha[:2])
            linha_dist = list()

            for valor in valores_linha:
                linha_dist.append(int(valor))

            mat_dist.append(linha_dist)

    return mat_dist, qtd_vendedor, coordenadas


def calcula_vetor_probabilidades(p_anterior, mat_dist, sol_parcial):
    # Faz uma cópia da linha de distâncias referente a p_anterior
    linha_dists = mat_dist[p_anterior][:]
    # Calcula a qualidade de cada distância e o vetor de probabilidades
    qtd_pontos = len(mat_dist)
    maior_dist = max(linha_dists) + 1  # Soma 1 para não dar divisão por zero
    linha_qualidade = [math.pow(maior_dist - linha_dists[i], 2) for i in range(qtd_pontos)]

    # Zera a qualidade dos pontos na solução parcial
    for ponto in sol_parcial:
        linha_qualidade[ponto] = 0
    qualidade_total = sum(linha_qualidade)
    try:
        vet_prob_individual = [linha_qualidade[i] / qualidade_total for i in range(qtd_pontos)]
    except:
        print(linha_dists)
        print(sol_parcial)
        print(linha_qualidade)
    # Calcula o vetor de probabilidade cumulativa
    vet_prob_cumulativa = [vet_prob_individual[0]]
    for prob in vet_prob_individual[1:]:
        vet_prob_cumulativa.append(vet_prob_cumulativa[-1] + prob)
    # Retorna o vetor de probabilidades cumulativas
    return vet_prob_cumulativa


# Função que gera as soluções aleatórias iniciais
def gera_solucao_aleatoria_v2(qtd_pontos, qtd_vendedores, mat_dist):
    # Gerando os pontos iniciais
    pontos = [i for i in range(qtd_pontos)]
    solucao_array = []
    for vndr in range(qtd_vendedores):
        # Gera um corte randomizado entre 0 - 2 para o corte do numero de pontos de uma solução 
        corte = rnd.randint(0, 2)
        rnd.shuffle(pontos)
        # Pega o primeiro ponto disponível para iniciar a solução
        solucao = [pontos[0]]
        # determinando a quantidade que vai ter a solução
        if(vndr == (qtd_vendedores - 1)):
            get_pontos = len(pontos)
        else:
            get_pontos = qtd_pontos // qtd_vendedores - corte
        
        # Gerando o restante da solução
        for i in range(get_pontos - 1):
            # Calcula o vetor de probabilidades cumulativas
            vet_prob = calcula_vetor_probabilidades(solucao[-1], mat_dist, solucao)
            
            # Sorteia um valor aleatório e define a posição correspondente
            r = rnd.random()
            idx = 0
            menor_resultado = float('inf')
            menor_resultado_id = 0
            while True:
                # Vai armazenando o melhor ponto disponivel para que seja adicionada as soluções
                if (menor_resultado > vet_prob[idx] and idx in pontos and idx not in solucao):
                    menor_resultado_id = vet_prob[idx]
                    menor_resultado_id = idx

                # Ao encontrar o melhor ponto correspondente finaliza o loop para adiciona-lo a solução
                if (vet_prob[idx] >= r and idx in pontos and idx not in solucao):
                    menor_resultado_id = idx
                    break

                # Finaliza o loop caso chgou ao fim do Array
                if(idx == (len(vet_prob) - 1)):
                    break
                idx += 1
            
            # Adicionando o ponto encontrado à solução
            solucao.append(menor_resultado_id)

        # Remove os pontos de uma solução dos pontos disponíveis para que o mesmo não seja repetido
        for i in solucao:
            pontos.remove(i)

        # Adiciona a solução ao array de soluções
        solucao_array.append(solucao)

    # Retorna a solução gerada
    return solucao_array

# V1 - Função da versão inicial
# Faz a geração de soluções aleatórias
def gera_solucao_aleatoria(qtd_pontos, qtd_vendedores):
    vet_pontos = [i for i in range(qtd_pontos)]
    rnd.shuffle(vet_pontos)

    rotas = []
    for _ in range(qtd_vendedores - 1):
        array_1 = rnd.randint(0, 2)
        rota_aux = rnd.sample(vet_pontos, int(
            qtd_pontos / qtd_vendedores) - array_1)
        rotas.append(rota_aux)
        for i in rota_aux:
            vet_pontos.remove(i)
    # Retornar a solução gerada
    return [vet_pontos] + rotas


# Calcula o custo total de uma determinada solução
def calcula_custo_solucao(solucao, mat_dist):
    # Armazena o custo total da solução
    custo_total = 0
    # Itera sobre todos os pontos e calcula a distância com relação ao próximo ponto
    for idx, anterior in enumerate(solucao[:-1]):
        proximo = solucao[idx + 1]
        distancia = mat_dist[anterior][proximo]
        custo_total += distancia
    # Somar a distância para retornar à origem
    anterior = solucao[-1]
    proximo = solucao[0]
    custo_total += mat_dist[anterior][proximo]
    # Retornar o custo total da solução
    return custo_total


# V1 - Função da versão inicial
# Faz a troca entre os pontos p1 e p2
def troca_pontos_solucao(sol_original, p1, p2):
    # Cria uma cópia da solução original
    nova_solucao = sol_original[:]
    nova_solucao[p1] = sol_original[p2]
    nova_solucao[p2] = sol_original[p1]
    # Retorna a solução gerada
    return nova_solucao


# Função de inversão do trecho do tipo 2-op
def inverte_trecho(solucao, p1, p2):
    # Copia o trecho entre 0 e p1 - 1
    nova_solucao = solucao[0:p1]
    # Trecho intermediário
    meio = solucao[p1:p2+1]
    meio.reverse()
    nova_solucao.extend(meio)
    # Trecho final
    nova_solucao.extend(solucao[p2+1:])
    # Retorna a solução
    return nova_solucao

# Gera todos os vizinhos possíveis de uma solução e retorna o melhor vizinho
def encontra_melhor_vizinho(sol_original, mat_dist):
    # Variaveis de armazenamento do melhor vzinho
    melhor_vizinho = None
    melhor_vizinho_valor = float('inf')

    qtd_pontos = len(sol_original)

    # Faz todas as trocas de pontos possíveis
    for p1 in range(qtd_pontos - 1):
        for p2 in range(p1 + 1, qtd_pontos):
            # V1 - Função da versão inicial - Troca de pontos próximos
            # novo_vizinho = troca_pontos_solucao(sol_original, p1, p2)
            novo_vizinho = inverte_trecho(sol_original, p1, p2)

            novo_vizinho_valor = calcula_custo_solucao(novo_vizinho, mat_dist)
            # Verificar se o novo vizinho é melhor que o melhor vizinho conhecido até o momento
            if novo_vizinho_valor < melhor_vizinho_valor:
                melhor_vizinho = novo_vizinho
                melhor_vizinho_valor = novo_vizinho_valor
    # Retorna o melhor vizinho e o seu valor
    return melhor_vizinho, melhor_vizinho_valor

# Encontra o ótimo local de uma solução utilizando a estrutura de vizinhança de troca de 2 pontos
def encontra_otimo_local(sol_inicial, mat_dist):
    # Armazena a solução no ótimo local
    sol_otimo_local = sol_inicial[:]
    sol_otimo_local_valor = calcula_custo_solucao(sol_otimo_local, mat_dist)

    otimo_local = False
    # Execução para gerar o ótimo local
    while not otimo_local:
        # Faz a busca do melhor vizinho com base na solução inicial
        melhor_viz, melhor_viz_valor = encontra_melhor_vizinho(sol_otimo_local, mat_dist)
        # Testa se o melhor vizinho é uma melhoria com relação ao melhor valor conhecido
        if melhor_viz_valor < sol_otimo_local_valor:
            sol_otimo_local = melhor_viz
            sol_otimo_local_valor = melhor_viz_valor
        else:
            # já foi encontrada a melhor solução
            otimo_local = True
    # Retornar o melhor vizinho encontrado e o custo dele
    return sol_otimo_local, sol_otimo_local_valor


# Função que salva o relatório no formato desejado
def salva_relatorio(relatorio, arq_relatorio):
    # Abre o arquivo
    with open(arq_relatorio, 'w+') as f:
        # Escreve os cabeçalhos
        f.write('ITERAÇÃO;INICIAL;LOCAL;GLOBAL\n')
        # Escreve todos os valores do relatorio
        for linha in relatorio:
            f.write("{};{};{};{}\n".format(
                linha[0], linha[1], linha[2], linha[3]))


# Função que salva a solução no arquivo
def salva_solucao(vet_solucao, custos, custo, qtd_pontos, arq_solucao):
    # Abre o arquivo
    with open(arq_solucao, 'w+') as f:
        # Salva a quantidade de pontos
        qtd_vendedores = len(vet_solucao)

        f.write("QTD_PONTOS;{}\n".format(qtd_pontos))
        f.write("QTD_VENDEDORES;{}\n".format(qtd_vendedores))
        f.write("MAIOR_CUSTO;{}\n".format(custo))
        f.write("VENDEDOR;CUSTO;SEQUÊNCIA\n")
        for i in range(len(vet_solucao)):
            f.write("V{};{};".format(i, custos[i]))
            for ponto in vet_solucao[i][:-1]:
                f.write("{};".format(ponto))
            # Salva o último ponto
            f.write("{}\n".format(vet_solucao[i][-1]))


# Executa as iterações do Hill-Climbing
def solver_hill_climbing(arq_instancia, qtd_iteracoes, arq_solucao, arq_relatorio):
    # Lê os dados do arquivo de instância
    mat_dist, qtd_vendedores, _ = le_dados_instancia(arq_instancia)

    qtd_pontos = len(mat_dist)
    # Armazena a melhor solução de todas as iterações
    melhor_global = None
    melhor_global_custo = None
    melhor_global_valor = float('inf')
    # Armazena o relatório de execução
    relatorio = list()
    # Executa todas as iterações do Hill-Climbing
    for iteracao in range(qtd_iteracoes):
        # Gera as N soluções inicial
        sol_candidata = gera_solucao_aleatoria_v2(qtd_pontos, qtd_vendedores, mat_dist)
        
        # Verifica qual é o pior custo dentre as soluções iniciais
        # para buscar melhorar a pior solução
        valor_inicial_iteracao = float('inf')
        for i, sol in enumerate(sol_candidata):
            valor = calcula_custo_solucao(sol, mat_dist)
            if valor < valor_inicial_iteracao:
                valor_inicial_iteracao = valor

        # Faz a busca para encontrar o melhor local das N soluções
        sol_candidata_valor = 0
        custos = []
        for i, solucao in enumerate(sol_candidata):
            sol_candidata[i], solucao_valor = encontra_otimo_local(solucao, mat_dist)
            custos.append(solucao_valor)
            # Identificando o pior local dentre os encontrados para ser comparado com o melhor global
            if(solucao_valor > sol_candidata_valor):
                sol_candidata_valor = solucao_valor

        # Testa se a pior solução encontrada atual melhorou em relação a encontrada anteriormente (melhor_global_valor)
        if sol_candidata_valor < melhor_global_valor:
            melhor_global = sol_candidata
            melhor_global_custo = custos
            melhor_global_valor = sol_candidata_valor

        # Informações para a geração do relatório
        valores_iteracao = (iteracao + 1, valor_inicial_iteracao, sol_candidata_valor, melhor_global_valor)
        relatorio.append(valores_iteracao)

    # Salvando os relatórios
    salva_relatorio(relatorio, arq_relatorio)
    salva_solucao(melhor_global, melhor_global_custo, melhor_global_valor, qtd_pontos, arq_solucao)

    return melhor_global, melhor_global_valor


# Chama a função que nós criamos
if __name__ == '__main__':
    # Pasta onde estão as soluções e relatórios
    dir_relatorios = 'mtsp_instances/relatorios/'
    dir_solucoes = 'mtsp_instances/solucoes/'
    # Pasta onde estão as instâncias
    dir_instancias = 'mtsp_instances/instancias/'
    # Lista com todos os arquivos de instância
    lista_instancias = os.listdir(dir_instancias)
    lista_instancias.sort()

    # Executa o Hill-Climbing para todas as instâncias
    cont_instancia = 1
    for arquivo in lista_instancias:
        nome_instancia = dir_instancias + arquivo
        nome_solucao = dir_solucoes + 'novo3_' + arquivo
        nome_relatorio = dir_relatorios + 'novo3_' + arquivo
        # Rodas o solver do Hill-Climbing
        t_ini = time.time()
        solucao, valor = solver_hill_climbing(nome_instancia, 1000, nome_solucao, nome_relatorio)
        t_fim = time.time()
        print("Instância {} ... OK - {:.04f} segundos".format(arquivo, t_fim - t_ini))