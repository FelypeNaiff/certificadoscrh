# Sistema de Certificados CRH

Aplicação web construída com Flask para emissão e validação de certificados de cursos. O sistema possui duas áreas principais:

- **Área administrativa** para gerar certificados a partir de um formulário e disponibilizar o PDF resultante com um código único de validação.
- **Área pública** para que alunos ou terceiros consultem a autenticidade do documento informando o código de validação impresso no certificado.

## Funcionalidades

- Emissão de certificados em PDF a partir dos dados informados no formulário administrativo.
- Armazenamento dos certificados emitidos em banco de dados SQLite, incluindo o arquivo PDF em formato binário.
- Geração automática de códigos de validação únicos.
- Listagem dos certificados emitidos, com detalhes e opção de download do PDF.
- Página pública para validação, com exibição dos dados do certificado e link direto para download quando o código for válido.

## Requisitos

- Python 3.11 ou superior.
- Ambiente virtual recomendado para isolar as dependências.

## Instalação e execução

1. Clone o repositório e acesse a pasta do projeto:

   ```bash
   git clone https://github.com/SEU_USUARIO/certificadoscrh.git
   cd certificadoscrh
   ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação em modo de desenvolvimento:

   ```bash
   flask --app app run --debug
   ```

   Na primeira execução o banco de dados `instance/certificates.sqlite` será criado automaticamente.

5. Acesse no navegador:

   - `http://localhost:5000/` — página pública para validação de certificados.
   - `http://localhost:5000/admin` — formulário administrativo para emissão.
   - `http://localhost:5000/admin/certificates` — lista de certificados emitidos.

### Configuração opcional

- Defina a variável de ambiente `VALIDATION_URL` para personalizar o endereço exibido nos certificados (por padrão é utilizada a URL gerada automaticamente pelo Flask, como `http://localhost:5000/`). Se desejar que o link inclua um caminho específico, informe, por exemplo, `https://seusite.com/validar`.

## Estrutura do projeto

```
app/
├── __init__.py        # Configuração da aplicação Flask e do banco de dados
├── models.py          # Definição do modelo de certificado
├── pdf.py             # Utilitário para geração do PDF
├── routes.py          # Rotas da área administrativa e pública
├── static/css/        # Arquivos de estilo
└── templates/         # Templates HTML do sistema
```

Os PDFs gerados são armazenados diretamente na tabela `certificates`. O download é realizado por meio de rotas autenticadas pelo código de validação.

## Próximos passos sugeridos

- Implementar autenticação para a área administrativa.
- Permitir personalizar o layout do certificado (logotipo, cores, assinaturas digitais).
- Integrar com um serviço de e-mail para envio automático do certificado ao aluno.
- Adicionar testes automatizados para as principais rotas.
