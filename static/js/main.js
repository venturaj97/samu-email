document.addEventListener('DOMContentLoaded', function() {

    //Seleção de Elementos
    const form = document.getElementById('emailForm');
    const emailTextInput = document.getElementById('email_text');
    const emailFileInput = document.getElementById('email_file');
    const cancelFileBtn = document.getElementById('cancelFileBtn');
    const cancelTextBtn = document.getElementById('cancelTextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const resultArea = document.getElementById('resultArea');
    const resultAlert = document.getElementById('resultAlert');
    const categoriaSpan = document.getElementById('categoria');
    const respostaP = document.getElementById('resposta');
    const errorArea = document.getElementById('errorArea');
    const copyBtn = document.getElementById('copyBtn');
    const sendEmailArea = document.getElementById('sendEmailArea');
    const sendEmailForm = document.getElementById('sendEmailForm');
    const recipientEmailInput = document.getElementById('recipientEmail');
    const sendStatus = document.getElementById('sendStatus');

    //Funções Auxiliares de UI
    function showLoading(isLoading) {
        if (isLoading) {
            btnText.textContent = 'Analisando...';
            btnSpinner.style.display = 'inline-block';
            submitBtn.disabled = true;
        } else {
            btnText.textContent = 'Analisar Agora';
            btnSpinner.style.display = 'none';
            submitBtn.disabled = false;
        }
    }
    
    function displayError(message) {
        errorArea.textContent = message;
        errorArea.style.display = 'block';
        resultArea.style.display = 'none';
    }

    function displayResults(data) {
        errorArea.style.display = 'none';
        categoriaSpan.textContent = data.categoria;
        respostaP.textContent = data.resposta_sugerida;
        
        resultAlert.className = 'alert';
        const alertClass = data.categoria === 'Produtivo' ? 'alert-success' : 'alert-warning';
        resultAlert.classList.add(alertClass);
        
        resultArea.style.display = 'block';
        resultArea.classList.add('fade-in');
        sendEmailArea.style.display = 'block'; 
        sendStatus.textContent = ''; // Limpa o status anterior
    }
    
    //Lógica de Interatividade do Formulário
    emailTextInput.addEventListener('input', () => {
        if (emailTextInput.value.trim()) {
            emailFileInput.value = '';
            emailFileInput.disabled = true;
            cancelFileBtn.style.display = 'none';
            cancelTextBtn.style.display = 'block';
            
        } else {
            emailFileInput.disabled = false;
            cancelTextBtn.style.display = 'none';
        }
    });

    emailFileInput.addEventListener('change', () => {
        if (emailFileInput.files.length > 0) {
            emailTextInput.value = '';
            emailTextInput.disabled = true;
            cancelFileBtn.style.display = 'block';
        } else {
            emailTextInput.disabled = false;
            cancelFileBtn.style.display = 'none';
        }
    });

    cancelFileBtn.addEventListener('click', () => {
        emailFileInput.value = null;
        emailFileInput.dispatchEvent(new Event('change')); 
    });
    
    cancelTextBtn.addEventListener('click', () => {
        emailTextInput.value = null;
        emailTextInput.dispatchEvent(new Event('input')); 
    });

    //Lógica de Submissão do Formulário
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        if (!emailTextInput.value.trim() && emailFileInput.files.length === 0) {
            displayError('Por favor, insira um texto ou selecione um arquivo para analisar.');
            return;
        }

        showLoading(true);
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/processar/', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json(); 

            if (!response.ok) {
                throw new Error(data.detail || 'Ocorreu um erro no servidor.');
            }
            displayResults(data);
        } catch (error) {
            console.error('Falha na requisição:', error);
            displayError('Não foi possível conectar ao servidor. Verifique se ele está rodando e tente novamente.');
        } finally {
            showLoading(false);
        }
    });

    sendEmailForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        const recipient = recipientEmailInput.value;
        const message = respostaP.textContent; // Pega a resposta da área de resultados

        if (!recipient) {
            sendStatus.textContent = 'Por favor, insira um email de destinatário.';
            sendStatus.className = 'form-text text-danger';
            return;
        }

        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = true;
        sendStatus.textContent = 'Enviando...';
        sendStatus.className = 'form-text text-muted';

        try {
            const response = await fetch('/api/enviar-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    destinatario: recipient,
                    mensagem: message
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Falha no envio.');
            }
            
            sendStatus.textContent = result.status;
            sendStatus.className = 'form-text text-success';

        } catch (error) {
            console.error('Erro ao enviar email:', error);
            sendStatus.textContent = 'Erro: ' + error.message;
            sendStatus.className = 'form-text text-danger';
        } finally {
            sendBtn.disabled = false;
        }
    });

    // A verificação 'if (copyBtn)' previne o erro se o botão não for encontrado
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(respostaP.textContent).then(() => {
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Erro ao copiar texto: ', err);
                alert('Não foi possível copiar o texto.');
            });
        });
    }
});