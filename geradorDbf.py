import dbf

import dbf

# Definir a estrutura da tabela
table = dbf.Table(
    'municipios_com_duplicatas.dbf',
    'CD_MUN C(7); NM_MUN C(50); CD_RGI C(6); NM_RGI C(20); CD_RGINT C(4); NM_RGINT C(20); '
    'CD_UF C(2); NM_UF C(20); CD_REGIAO C(1); NM_REGIAO C(10); '
    'CD_CONCURB C(7); NM_CONCURB C(30); AREA_KM2 C(15)',
    codepage='utf8'
)

# Criar a tabela
table.open(mode=dbf.READ_WRITE)

# Dados dos municípios (com algumas duplicatas propositais)
dados = [
    # Dados originais
    ("1100015", "Alta Floresta D'Oeste", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "7067,127"),
    ("1100023", "Ariquemes", "110002", "Ariquemes", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "4426,143"),
    ("1100031", "Cabixi", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1314,352"),
    ("1100049", "Cacoal", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "3793,000"),
    ("1100056", "Cerejeiras", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "2783,297"),
    
    # Primeira duplicata - repetindo Ariquemes
    ("1100023", "Ariquemes", "110002", "Ariquemes", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "4426,143"),
    
    ("1100064", "Colorado do Oeste", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1451,063"),
    ("1100072", "Corumbiara", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "3060,321"),
    ("1100080", "Costa Marques", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "4987,177"),
    ("1100098", "Espigão D'Oeste", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "4518,038"),
    
    # Segunda duplicata - repetindo Cacoal
    ("1100049", "Cacoal", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "3793,000"),
    
    ("1100106", "Guajará-Mirim", "110001", "Porto Velho", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "24856,877"),
    ("1100114", "Jaru", "110003", "Jaru", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "2944,140"),
    ("1100122", "Ji-Paraná", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "1100122", "Ji-Paraná", "6896,649"),
    
    # Terceira duplicata - repetindo Ji-Paraná
    ("1100122", "Ji-Paraná", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "1100122", "Ji-Paraná", "6896,649"),
    
    ("1100130", "Machadinho D'Oeste", "110003", "Jaru", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "8509,270"),
    ("1100148", "Nova Brasilândia D'Oeste", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1703,008"),
    ("1100155", "Ouro Preto do Oeste", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1969,879"),
    
    # Quarta duplicata - repetindo Ouro Preto do Oeste
    ("1100155", "Ouro Preto do Oeste", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1969,879"),
    
    ("1100189", "Pimenta Bueno", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "6241,019"),
    ("1100205", "Porto Velho", "110001", "Porto Velho", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "1100205", "Porto Velho/RO", "34091,146"),
    
    # Quinta duplicata - repetindo Porto Velho
    ("1100205", "Porto Velho", "110001", "Porto Velho", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "1100205", "Porto Velho/RO", "34091,146"),
    
    ("1100254", "Presidente Médici", "110004", "Ji-Paraná", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1758,464"),
    ("1100262", "Rio Crespo", "110002", "Ariquemes", "1101", "Porto Velho", "11", "Rondônia", "1", "Norte", "", "", "1717,640"),
    ("1100288", "Rolim de Moura", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1457,812"),
    
    # Sexta duplicata - repetindo Rolim de Moura
    ("1100288", "Rolim de Moura", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1457,812"),
    
    ("1100296", "Santa Luzia D'Oeste", "110005", "Cacoal", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "1197,796"),
    ("1100304", "Vilhena", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "11708,579"),
    
    # Sétima duplicata - repetindo Vilhena
    ("1100304", "Vilhena", "110006", "Vilhena", "1102", "Ji-Paraná", "11", "Rondônia", "1", "Norte", "", "", "11708,579"),
    
    # Mais alguns municípios do Acre para completar
    ("1200013", "Acrelândia", "120001", "Rio Branco", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "1811,621"),
    ("1200054", "Assis Brasil", "120002", "Brasiléia", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "4977,815"),
    ("1200104", "Brasiléia", "120002", "Brasiléia", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "3928,820"),
    
    # Oitava duplicata - repetindo Brasiléia
    ("1200104", "Brasiléia", "120002", "Brasiléia", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "3928,820"),
    
    ("1200138", "Bujari", "120001", "Rio Branco", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "3035,547"),
    ("1200179", "Capixaba", "120001", "Rio Branco", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "1705,236"),
    ("1200203", "Cruzeiro do Sul", "120004", "Cruzeiro do Sul", "1202", "Cruzeiro do Sul", "12", "Acre", "1", "Norte", "", "", "8782,922"),
    
    # Nona duplicata - repetindo Cruzeiro do Sul
    ("1200203", "Cruzeiro do Sul", "120004", "Cruzeiro do Sul", "1202", "Cruzeiro do Sul", "12", "Acre", "1", "Norte", "", "", "8782,922"),
    
    ("1200252", "Epitaciolândia", "120002", "Brasiléia", "1201", "Rio Branco", "12", "Acre", "1", "Norte", "", "", "1652,715"),
    ("1200302", "Feijó", "120005", "Tarauacá", "1202", "Cruzeiro do Sul", "12", "Acre", "1", "Norte", "", "", "27977,120"),
    
    # Décima duplicata - repetindo Feijó
    ("1200302", "Feijó", "120005", "Tarauacá", "1202", "Cruzeiro do Sul", "12", "Acre", "1", "Norte", "", "", "27977,120"),
]

# Adicionar os registros à tabela
for registro in dados:
    table.append(registro)

# Fechar a tabela
table.close()

print("Arquivo 'municipios_com_duplicatas.dbf' criado com sucesso!")
print(f"Total de registros: {len(dados)}")
print(f"Registros únicos: {len(set(dados))}")
print("\nDuplicatas criadas:")
print("- Ariquemes (2x)")
print("- Cacoal (2x)") 
print("- Ji-Paraná (2x)")
print("- Ouro Preto do Oeste (2x)")
print("- Porto Velho (2x)")
print("- Rolim de Moura (2x)")
print("- Vilhena (2x)")
print("- Brasiléia (2x)")
print("- Cruzeiro do Sul (2x)")
print("- Feijó (2x)")