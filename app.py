import os
from flask import Flask, render_template, request, flash
import dbf
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'dbf'

def read_dbf_file(file_path):
    """Lê arquivo DBF e retorna os dados sem usar pandas"""
    try:
        table = dbf.Table(file_path)
        table.open()
        
        # Lê todos os registros
        data = []
        for record in table:
            # Converte o registro para dicionário
            record_dict = {}
            for field_name in record._field_names:
                record_dict[field_name] = record[field_name]
            data.append(record_dict)
        
        # Obtém os nomes das colunas da estrutura da tabela
        columns = [field.name for field in table.structure()]
        
        table.close()
        
        return data, columns, None
        
    except Exception as e:
        return None, None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    columns = []
    filename = None
    
    if request.method == 'POST':
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return render_template('index.html', data=data, columns=columns, filename=filename)
        
        file = request.files['file']
        
        # Verifica se o arquivo tem nome
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return render_template('index.html', data=data, columns=columns, filename=filename)
        
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
                else:
                    flash(f'Arquivo {filename} carregado com sucesso! '
                          f'({len(data)} registros, {len(columns)} colunas)', 'success')
                
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
    
    return render_template('index.html', data=data, columns=columns, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)