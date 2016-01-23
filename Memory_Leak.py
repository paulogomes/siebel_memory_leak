# -*- coding: iso-8859-1 -*-
import re
from glob import glob

dicionario = {}

def IncluiVariaveis(linha, metodo):
        global dicionario
        linha = linha.replace(',', ' ')
        linha = re.sub('\(.*\)', '', linha)
        lista = linha.split()
        lista.pop(0)
        for item in lista:
                if re.search('^as$', item, flags=re.IGNORECASE):
                        for variavel in lista[0:lista.index(item)]:
                                dicionario[variavel] = {'Tipo': lista[lista.index(item)+1],'Status': 'Definida', 'metodo': metodo, 'filho': None}
                        lista = lista[lista.index(item)+2:]

def atualiza(nome, tipo=None, status=None, nome_metodo=None, filho=None):
        global dicionario
        if (nome in dicionario):
                if (tipo):
                        dicionario[nome]['Tipo'] = tipo
                if (status):
                        dicionario[nome]['Status'] = status
                if (nome_metodo):
                        dicionario[nome]['metodo'] = nome_metodo
                if (filho):
                        dicionario[nome]['filho'] = filho

def VariaveisDoMetodo(metodos):
        global dicionario
        for key,value in dicionario.items():
                for k,v in value.items():
                        for metodo in metodos:
                                if metodo==v:
                                        yield key

def procces_file(linhas, objeto, nome_objeto, arquivo):

        global dicionario
        dicionario.clear()
        metodo = ''

        for linha in linhas:
                #print linha
                if (re.search('[\'].*|theApplication.trace', linha, flags=re.IGNORECASE)):
                        continue
                # Procura definição de variaveis
                elif (re.search('^[ \t]*dim+[\ ].*', linha, flags=re.IGNORECASE)):
                        IncluiVariaveis(linha, metodo)
        
                # Procura definição de Subrotina ou Função
                elif (re.search('^[ \t]*sub+[\ ].*|^[ \t]*Function+[\ ].*', linha, flags=re.IGNORECASE)):
                        linha = re.sub('\(.*', '', linha)
                        variaveis = linha.split()
                        metodo = variaveis[1]
        
                # Procura fechamento da Subrotina ou Função
                elif (re.search('^[ \t]*end sub*|^[ \t]*end function*', linha, flags=re.IGNORECASE)):
                        for var in VariaveisDoMetodo([metodo]):
                                if (re.search('BusComp|BusObject|PropertySet|Service', dicionario[var]['Tipo'], flags=re.IGNORECASE)):
                                        if dicionario[var]['Status'] not in ['Fechada']:
                                                arquivo.write(';'.join([objeto, nome_objeto, dicionario[var]['metodo'], var, dicionario[var]['Tipo'], dicionario[var]['Status']])+'\n')
                        metodo = ''
                
                if (re.search('.*=.*', linha)):
                        for var in VariaveisDoMetodo([metodo, '']):
                                if (re.search('BusComp|BusObject|PropertySet|Service', dicionario[var]['Tipo'], flags=re.IGNORECASE)):
                                        if (re.search(var+'[ \t]*=[ \t]*Nothing', linha, flags=re.IGNORECASE)):
                                                if(dicionario[var]['Tipo']=='BusObject' and dicionario[var]['filho']):
                                                        filho = dicionario[var]['filho']
                                                        if (filho in dicionario and dicionario[filho]['Status'] != 'Fechada'):
                                                                dicionario[var]['Status'] = 'Fechada antes do filho'
                                                                continue
                                                dicionario[var]['Status'] = 'Fechada'
                                        if (dicionario[var]['Tipo']=='BusObject'):
                                                if (re.search(var+'.*GetBusComp', linha, flags=re.IGNORECASE)):
                                                          a = linha.split()
                                                          atualiza(var, filho=a[1])
                                if dicionario[var]['Status'] == 'Definida':
                                        if (re.search(var+'*=', linha)):
                                                dicionario[var]['Status'] = 'Utilizada'


        for var in VariaveisDoMetodo(['']):
                if (re.search('BusComp|BusObject|PropertySet|Service', dicionario[var]['Tipo'], flags=re.IGNORECASE)):
                        if dicionario[var]['Status'] not in ['Fechada']:
                                arquivo.write(';'.join([objeto, nome_objeto, dicionario[var]['metodo'], var, dicionario[var]['Tipo'], dicionario[var]['Status']])+'\n')


root = "C:/codigo/Memory_Leak/Analise"
arquivos = glob(root+'*/*/*.sbl')
print arquivos
log = file(root+'log.csv', 'w')
log.write('Objeto;Nome;Metodo;variavel;Tipo;Status\n')
for nomearquivo in arquivos:
        objeto = nomearquivo.split('/')
        arquivo = file(nomearquivo, 'r')
        linhas = [ linha for linha in arquivo ]
        i = objeto[-1].replace('.sbl', '')
        print 'Processando: ' + i 
        procces_file(linhas, objeto[-2], i, log)
        arquivo.close()