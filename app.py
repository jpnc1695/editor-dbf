import os
from flask import Flask, render_template, request, flash
from dbfread import DBF, DBFNotFound
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'dbf'

def read_dbf_file(file_path):
    """Lê arquivo DBF usando dbfread (mais confiável)"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            return None, None, "Arquivo não encontrado"
        
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
                    if i >= 1000:  # Limite para performance
                        break
                
                return data, columns, None
                
            except UnicodeDecodeError:
                continue  # Tenta próxima codificação
            except Exception as e:
                continue  # Tenta próxima codificação
        
        return None, None, "Não foi possível ler o arquivo com nenhuma codificação"
        
    except Exception as e:
        return None, None, f"Erro ao processar arquivo DBF: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    columns = None
    filename = None
    record_count = 0
    column_count = 0
    
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return render_template('index.html', 
                                 data=data, 
                                 columns=columns, 
                                 filename=filename,
                                 record_count=record_count,
                                 column_count=column_count)
        
        file = request.files['file']
        
        # Verifica se o arquivo tem nome
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return render_template('index.html', 
                                 data=data, 
                                 columns=columns, 
                                 filename=filename,
                                 record_count=record_count,
                                 column_count=column_count)
        
        # Verifica se é um arquivo DBF
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # Salva o arquivo
                file.save(file_path)
                
                # Lê o arquivo DBF
                data, columns, error = read_dbf_file(file_path)
                
                if error:
                    flash(f'Erro ao ler arquivo: {error}', 'error')
                elif data is not None and columns is not None:
                    record_count = len(data)
                    column_count = len(columns)
                    flash(f'Arquivo {filename} carregado com sucesso! '
                          f'({record_count} registros, {column_count} colunas)', 'success')
                else:
                    flash('Não foi possível ler os dados do arquivo', 'error')
                
                # Remove o arquivo temporário
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}', 'error')
                # Remove o arquivo em caso de erro
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash('Por favor, selecione um arquivo .dbf', 'error')
    
    return render_template('index.html', 
                         data=data, 
                         columns=columns, 
                         filename=filename,
                         record_count=record_count,
                         column_count=column_count)

if __name__ == '__main__':
    app.run(debug=True)