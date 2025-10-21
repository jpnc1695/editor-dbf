import os
from flask import Flask, render_template, request, flash, session, redirect
from dbfread import DBF
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__)

# 🔒 CONFIGURAÇÃO PARA PRODUÇÃO (RAILWAY)
# Remove qualquer referência ao .env e usa apenas variáveis de ambiente
app.secret_key = os.environ.get('SECRET_KEY')

# Verifica se a SECRET_KEY foi configurada corretamente
if not app.secret_key:
    print("❌ ERRO: SECRET_KEY não encontrada nas variáveis de ambiente!")
    print("💡 No Railway, vá em Variables → Add SECRET_KEY")
    # Fallback apenas para evitar crash, mas NÃO USE EM PRODUÇÃO
    app.secret_key = 'fallback-temporary-key-railway-' + os.urandom(16).hex()

# Configurações do Flask
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Log para verificar se a SECRET_KEY foi carregada
print(f"🔑 SECRET_KEY configurada: {'✅ SIM' if app.secret_key and app.secret_key.startswith('ac883') else '❌ NÃO'}")
print(f"🌐 Ambiente: {'🚀 PRODUÇÃO' if 'RAILWAY' in os.environ else '💻 DESENVOLVIMENTO'}")

# ... (o resto do seu código permanece igual) ...

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dbf'

def read_dbf_file(file_path):
    """Lê arquivo DBF usando dbfread"""
    try:
        if not os.path.exists(file_path):
            return None, None, "Arquivo não encontrado"
        
        encodings = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                table = DBF(file_path, encoding=encoding, char_decode_errors='ignore')
                columns = [field.name for field in table.fields]
                
                data = []
                for record in table:
                    record_dict = {}
                    for key, value in record.items():
                        if value is None:
                            record_dict[key] = None
                        elif isinstance(value, (bytes, bytearray)):
                            try:
                                record_dict[key] = value.decode('latin-1')
                            except:
                                record_dict[key] = str(value)
                        else:
                            record_dict[key] = value
                    data.append(record_dict)
                
                return data, columns, None
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        return None, None, "Não foi possível ler o arquivo com nenhuma codificação"
        
    except Exception as e:
        return None, None, f"Erro ao processar arquivo DBF: {str(e)}"

def encontrar_duplicados(data, coluna_chave='CD_MUN'):
    """Encontra registros duplicados"""
    if not data or not coluna_chave:
        return []
    
    contador = Counter()
    for registro in data:
        chave = registro.get(coluna_chave)
        if chave is not None:
            contador[str(chave)] += 1
    
    duplicados = []
    for registro in data:
        chave = registro.get(coluna_chave)
        if chave is not None and contador[str(chave)] > 1:
            registro_com_contagem = registro.copy()
            registro_com_contagem['_CONTAGEM_DUPLICATAS'] = contador[str(chave)]
            duplicados.append(registro_com_contagem)
    
    return duplicados

@app.route('/', methods=['GET', 'POST'])
def index():
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
                        flash(f'Arquivo {filename} carregado! ({record_count} registros, {column_count} colunas)', 'success')
                        
                        session['data'] = data
                        session['columns'] = columns
                        session['filename'] = filename
                        session['record_count'] = record_count
                        session['column_count'] = column_count
                        session['mostrar_duplicados'] = False
                    else:
                        flash('Não foi possível ler os dados', 'error')
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    flash(f'Erro: {str(e)}', 'error')
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                flash('Selecione um arquivo .dbf', 'error')
        
        elif 'mostrar_duplicados' in request.form:
            data = session.get('data')
            columns = session.get('columns')
            
            if data and columns:
                coluna_filtro = request.form.get('coluna_filtro', 'CD_MUN')
                session['coluna_filtro'] = coluna_filtro
                
                duplicados = encontrar_duplicados(data, coluna_filtro)
                record_count = len(duplicados)
                
                if duplicados:
                    flash(f'Encontrados {record_count} registros duplicados em {coluna_filtro}', 'info')
                    columns_com_contagem = columns + ['_CONTAGEM_DUPLICATAS']
                    
                    session['data_filtrado'] = duplicados
                    session['columns_filtrado'] = columns_com_contagem
                    session['mostrar_duplicados'] = True
                    session['record_count'] = record_count
                    
                    data = duplicados
                    columns = columns_com_contagem
                else:
                    flash('Nenhum registro duplicado encontrado', 'info')
            else:
                flash('Carregue um arquivo primeiro', 'error')
        
        elif 'mostrar_todos' in request.form:
            data = session.get('data')
            columns_originais = session.get('columns')
            
            if data and columns_originais:
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
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)