# Reserva de Salas - MPGO 📅

Um sistema web ágil e moderno para reserva e gerenciamento de salas de reunião, construído com **Django** no backend e uma interface dinâmica alimentada por **FullCalendar** + **Bootstrap 5** no frontend.

## 🚀 Funcionalidades

- **Calendário Dinâmico:** Visualização semanal/mensal de reservas com bloqueio automático contra choques de horário e sobreposições para a mesma sala.
- **Filtro de Salas:** Possibilidade de visualizar a agenda de apenas uma sala por vez usando filtros de re-renderização assíncrona.
- **Color-Coding Inteligente:** As salas são categorizadas com paletas de cores pastéis automaticamente geradas para fácil identificação num piscar de olhos.
- **Gestão de Perfil:** O próprio usuário pode se registrar e atualizar os seus dados (Sala, Ramal, Senha) a qualquer momento.
- **Permissões de Acesso (Staff):** Administradores (staff) podem cancelar reservas alheias para gerir melhor o fluxo.
- **UI Responsiva & UX Refinada:** Interface projetada para ser simples, limpa e utilizável em qualquer resolução de tela (com foco em secretarias e administradores), contando com transições e *glassmorphism* em Modais de detalhes.

---

## 🛠️ Tecnologias Principais

- **Linguagem / Framework:** Python (Django)
- **Frontend:** Javascript Nativo (Vanilla JS), FullCalendar v6, Bootstrap 5.3
- **Banco de Dados:** SQLite (configuração padrão Django)
- **Gerenciador de Pacotes:** Padrão via Pip ou gerenciador acelerado (`uv`)

---

## ⚙️ Instalação e Execução (Passo a Passo)

Siga os passos abaixo para rodar o projeto do zero na sua máquina local. 

### 1. Clonar e preparar o ambiente
Abra o seu terminal no diretório do projeto e ative um ambiente virtual.
*(Dado o uso do `uv.lock`, recomendamos usar o pacote `uv` caso já possua, ou o `venv` tradicional)*:

```powershell
# Criação de VENV tradicional (Windows)
python -m venv .venv

# Ativando o ambiente virtual no Windows:
.venv\Scripts\Activate.ps1
```

### 2. Instalar as Dependências
```powershell
# Se for usar PIP
pip install django
# Ou via pacote uv (se tiver uv instalado):
uv sync
```

### 3. Executar as Migrações de Banco de Dados
Para o sistema construir as tabelas do **Cadastro de Usuários**, **Salas** e **Reservas**:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Rodar o Servidor
Com tudo preparado, ligue o servidor web de desenvolvimento do próprio Django:
```bash
python manage.py runserver
```

Acesse o sistema por meio do link no seu navegador: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Criando um Administrador (Superusuário)

Para cadastrar as Salas de Reunião iniciais e gerenciar qualquer reserva feita por outras pessoas, é preciso ter uma conta com permissões administrativas.

**Para criá-la**, com seu ambiente virtual ativado, rode no terminal:
```bash
python manage.py createsuperuser
```

1. O terminal vai pedir um `Username` (Nome de Usuário) — *Recomendação: utilize um endereço de email ou admin*.
2. Em seguida, vai pedir o `Email` associado (opcional).
3. Depois exigirá uma `Password` (Senha) e a confirmação dela. *(Nota: Por padrão de segurança do terminal, ao digitar a senha, ela ficará invisível, não aparecerá nenhuma borboleta ou caractere, apenas continue digitando e aperte ENTER).*

**Acessando a Área Administrativa:**  
Com sua aplicação rodando (`runserver`), vá em seu navegador até `http://127.0.0.1:8000/admin`. 
Faça o login com as credenciais acima. É por aqui que você deve cadastrar as primeiras `Salas`! Após adicioná-las no painel Admin, elas aparecerão com suas respectivas cores lá no calendário público inicial para reserva.
