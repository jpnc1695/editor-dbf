import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, session, redirect
from dbfread import DBF
from werkzeug.utils import secure_filename
from collections import Counter
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# No Railway, podemos usar um diretório temporário para uploads, mas note que é volátil.
# Vamos usar o diretório temporário do sistema.
app.config['UPLOAD_FOLDER'] = '/tmp'  # Railway permite escrever em /tmp

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dbf'

def read_dbf_file(file_path):
    """Lê arquivo DBF usando dbfread"""
    try:
        # Tenta ler com diferentes codificações
        encodings = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                table = DBF(file_path, encoding=encoding, char_decode_errors='ignore')
                
                # Obtém colunas
                columns = [field.name for field in table.fields]
                
                # Lê dados (limita a 1000 registros para performance)
                data = []
                for i, record in enumerate(table):
                    data.append(dict(record))
                    if i >= 1000:
                        break
                
                return data, columns, None
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        return None, None, "Não foi possível ler o arquivo com nenhuma codificação"
        
    except Exception as e:
        return None, None, f"Erro ao processar arquivo DBF: {str(e)}"

def encontrar_duplicados(data, coluna_chave='CD_MUN'):
    """Encontra registros duplicados baseado em uma coluna chave"""
    if not data or not coluna_chave:
        return []
    
    contador = Counter()
    for registro in data:
        chave = registro.get(coluna_chave)
        if chave is not None:
            contador[chave] += 1
    
    duplicados = []
    for registro in data:
        chave = registro.get(coluna_chave)
        if chave is not None and contador[chave] > 1:
            registro_com_contagem = registro.copy()
            registro_com_contagem['_CONTAGEM_DUPLICATAS'] = contador[chave]
            duplicados.append(registro_com_contagem)
    
    return duplicados

@app.route('/', methods=['GET', 'POST'])
def index():
    # Inicializa as variáveis a partir da sessão, se existirem
    data = session.get('data')
    columns = session.get('columns')
    filename = session.get('filename')
    record_count = session.get('record_count', 0)
    column_count = session.get('column_count', 0)
    mostrar_duplicados = session.get('mostrar_duplicados', False)
    coluna_filtro = session.get('coluna_filtro', 'CD_MUN')
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                flash('Nenhum arquivo selecionado', 'error')
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    file.save(file_path)
                    data, columns, error = read_dbf_file(file_path)
                    
                    if error:
                        flash(f'Erro ao ler arquivo: {error}', 'error')
                    elif data is not None and columns is not None:
                        record_count = len(data)
                        column_count = len(columns)
                        flash(f'Arquivo {filename} carregado com sucesso! ({record_count} registros, {column_count} colunas)', 'success')
                        
                        session['data'] = data
                        session['columns'] = columns
                        session['filename'] = filename
                        session['record_count'] = record_count
                        session['column_count'] = column_count
                        session['mostrar_duplicados'] = False
                    else:
                        flash('Não foi possível ler os dados do arquivo', 'error')
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    flash(f'Erro ao processar arquivo: {str(e)}', 'error')
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                flash('Por favor, selecione um arquivo .dbf', 'error')
        
        elif 'mostrar_duplicados' in request.form:
            data = session.get('data')
            columns = session.get('columns')
            
            if data and columns:
                coluna_filtro = request.form.get('coluna_filtro', 'CD_MUN')
                session['coluna_filtro'] = coluna_filtro
                
                duplicados = encontrar_duplicados(data, coluna_filtro)
                record_count = len(duplicados)
                
                if duplicados:
                    flash(f'Encontrados {record_count} registros duplicados baseados na coluna {coluna_filtro}', 'info')
                    
                    if '_CONTAGEM_DUPLICATAS' not in columns:
                        columns = columns + ['_CONTAGEM_DUPLICATAS']
                    
                    session['data_filtrado'] = duplicados
                    session['columns_filtrado'] = columns
                    session['mostrar_duplicados'] = True
                    session['record_count'] = record_count
                    
                    data = duplicados
                else:
                    flash('Nenhum registro duplicado encontrado', 'info')
                    session['mostrar_duplicados'] = False
            else:
                flash('Nenhum arquivo carregado para filtrar', 'error')
        
        elif 'mostrar_todos' in request.form:
            data = session.get('data')
            columns_originais = session.get('columns')
            
            if data and columns_originais:
                columns = [col for col in columns_originais if col != '_CONTAGEM_DUPLICATAS']
                
                record_count = len(data)
                flash(f'Mostrando todos os {record_count} registros', 'info')
                
                session['data_filtrado'] = None
                session['columns_filtrado'] = None
                session['mostrar_duplicados'] = False
                session['record_count'] = record_count
                
                data = data
                columns = columns_originais
            else:
                flash('Nenhum arquivo carregado', 'error')
    
    if session.get('mostrar_duplicados') and session.get('data_filtrado'):
        data = session['data_filtrado']
        columns = session['columns_filtrado']
        mostrar_duplicados = True
        record_count = len(data)
        column_count = len(columns)
    
    return render_template('index.html', 
                         data=data, 
                         columns=columns, 
                         filename=filename,
                         record_count=record_count,
                         column_count=column_count,
                         mostrar_duplicados=mostrar_duplicados,
                         coluna_filtro=coluna_filtro)

@app.route('/limpar', methods=['POST'])
def limpar_sessao():
    session.clear()
    flash('Sessão limpa. Faça upload de um novo arquivo.', 'info')
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)