// Configurações
const API_BASE = window.location.origin + '/api';

// Elementos do DOM
const elements = {
    cpfInput: document.getElementById('cpf'),
    generateBtn: document.getElementById('generateBtn'),
    loadingSection: document.getElementById('loadingSection'),
    successSection: document.getElementById('successSection'),
    errorSection: document.getElementById('errorSection'),
    clientInfo: document.getElementById('clientInfo'),
    errorDetails: document.getElementById('errorDetails'),
    newSearchBtn: document.getElementById('newSearchBtn'),
    tryAgainBtn: document.getElementById('tryAgainBtn')
};

// Estado da aplicação
let isLoading = false;
let currentTaskId = null;
let pollingInterval = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupCpfFormatting();
    elements.cpfInput.focus();
});

function setupEventListeners() {
    if (elements.generateBtn) {
        elements.generateBtn.addEventListener('click', handleGenerate);
    }
    
    if (elements.newSearchBtn) {
        elements.newSearchBtn.addEventListener('click', resetForm);
    }
    
    if (elements.tryAgainBtn) {
        elements.tryAgainBtn.addEventListener('click', resetForm);
    }
    
    if (elements.cpfInput) {
        elements.cpfInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isLoading) {
                handleGenerate();
            }
        });
    }
}

function setupCpfFormatting() {
    if (!elements.cpfInput) return;
    
    elements.cpfInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{1})$/, '$1.$2.$3-$4');
            value = value.replace(/(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3');
            value = value.replace(/(\d{3})(\d{1})$/, '$1.$2');
        }
        
        e.target.value = value;
    });
}

async function handleGenerate() {
    if (isLoading) return;
    
    const cpf = elements.cpfInput.value.trim();
    
    if (!validateCpf(cpf)) {
        elements.cpfInput.focus();
        return;
    }
    
    const cpfClean = cpf.replace(/\D/g, '');
    
    setLoading(true);
    showSection('loadingSection');
    
    try {
        const response = await fetch(`${API_BASE}/buscar-e-gerar-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cpf: cpfClean }),
            signal: AbortSignal.timeout(120000) // 2 minutos de timeout
        });
        
        let result;
        let responseText = '';
        
        try {
            // Primeiro, tentar ler como texto para debug
            responseText = await response.text();
            console.log('Response status:', response.status);
            console.log('Response text:', responseText);
            
            // Tentar parsear como JSON
            try {
                if (!responseText || responseText.trim() === '') {
                    console.error('Response vazia - Status:', response.status);
                    if (response.status === 502) {
                        displayError({
                            message: 'Servidor temporariamente indisponível',
                            details: {
                                tipo: 'BAD_GATEWAY',
                                descricao: 'O servidor está sobrecarregado',
                                detalhes: [
                                    'Tente novamente em alguns instantes',
                                    'O sistema pode estar processando outras requisições',
                                    'Se o problema persistir, aguarde alguns minutos'
                                ]
                            }
                        });
                    } else {
                        displayError({
                            message: 'Resposta vazia do servidor',
                            details: {
                                tipo: 'EMPTY_RESPONSE',
                                descricao: 'O servidor não retornou dados',
                                detalhes: [
                                    'Verifique sua conexão com a internet',
                                    'Tente novamente em alguns instantes',
                                    'Se o problema persistir, contate o suporte'
                                ]
                            }
                        });
                    }
                    return;
                }
                result = JSON.parse(responseText);
            } catch (parseError) {
                console.error('Erro ao parsear JSON:', parseError);
                console.error('Response text:', responseText);
                
                if (responseText.includes('<html>')) {
                    displayError({
                        message: 'Erro interno do servidor',
                        details: {
                            tipo: 'HTML_RESPONSE',
                            descricao: 'O servidor retornou uma página de erro',
                            detalhes: [
                                'O servidor pode estar sobrecarregado',
                                'Tente novamente em alguns instantes',
                                'Se o problema persistir, aguarde alguns minutos'
                            ]
                        }
                    });
                } else {
                    displayError({
                        message: 'Erro de comunicação com o servidor',
                        details: {
                            tipo: 'PARSE_ERROR',
                            descricao: 'Não foi possível interpretar a resposta do servidor',
                            detalhes: [
                                'Verifique sua conexão com a internet',
                                'Tente novamente em alguns instantes',
                                'Se o problema persistir, contate o suporte'
                            ]
                        }
                    });
                }
                return;
            }
        } catch (error) {
            console.error('Erro ao ler response:', error);
            displayError({
                message: 'Erro de conexão',
                details: {
                    tipo: 'FETCH_ERROR',
                    descricao: 'Não foi possível conectar com o servidor',
                    detalhes: [
                        'Verifique sua conexão com a internet',
                        'Certifique-se de que o servidor está funcionando',
                        'Tente novamente em alguns instantes'
                    ]
                }
            });
            return;
        }
        
        if (response.status === 200 && result.success) {
            if (result.status === 'PROCESSING' && result.task_id) {
                // Processamento assíncrono iniciado
                currentTaskId = result.task_id;
                startPolling(result.task_id);
            } else {
                // Resultado imediato (cache)
                displaySuccess(result);
            }
        } else {
            displayError({
                message: result.message || 'Erro desconhecido',
                details: result.details || {
                    tipo: 'API_ERROR',
                    descricao: 'Erro retornado pela API',
                    detalhes: [
                        'Verifique os dados informados',
                        'Tente novamente em alguns instantes',
                        'Se o problema persistir, contate o suporte'
                    ]
                }
            });
        }
        
    } catch (error) {
        console.error('Erro na requisição:', error);
        
        let errorMessage = 'Erro de conexão';
        let errorDetails = {
            tipo: 'NETWORK_ERROR',
            descricao: 'Não foi possível conectar com o servidor',
            detalhes: [
                'Verifique sua conexão com a internet',
                'Certifique-se de que o servidor está funcionando',
                'Tente novamente em alguns instantes'
            ]
        };
        
        if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
            errorMessage = 'Tempo limite excedido';
            errorDetails = {
                tipo: 'TIMEOUT',
                descricao: 'A requisição demorou muito para responder',
                detalhes: [
                    'O servidor pode estar sobrecarregado',
                    'A geração do PDF pode estar demorando',
                    'Tente novamente em alguns instantes',
                    'Se o problema persistir, aguarde alguns minutos'
                ]
            };
        } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = 'Erro de conexão';
            errorDetails = {
                tipo: 'FETCH_ERROR',
                descricao: 'Não foi possível conectar com o servidor',
                detalhes: [
                    'Verifique sua conexão com a internet',
                    'Certifique-se de que o servidor está funcionando',
                    'Tente novamente em alguns instantes'
                ]
            };
        }
        
        displayError({
            message: errorMessage,
            details: errorDetails
        });
    } finally {
        setLoading(false);
    }
}

async function startPolling(taskId) {
    console.log(`Iniciando polling para task: ${taskId}`);
    
    // Limpar polling anterior se existir
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    let attempts = 0;
    const maxAttempts = 120; // 10 minutos (5s * 120)
    
    pollingInterval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`${API_BASE}/task-status/${taskId}`);
            const result = await response.json();
            
            console.log(`Polling attempt ${attempts}:`, result);
            
            if (result.success) {
                if (result.state === 'SUCCESS') {
                    // Task concluída com sucesso
                    clearInterval(pollingInterval);
                    displaySuccess(result.result);
                } else if (result.state === 'FAILURE') {
                    // Task falhou
                    clearInterval(pollingInterval);
                    displayError({
                        message: result.message || 'Erro no processamento',
                        details: {
                            tipo: 'TASK_FAILURE',
                            descricao: 'O processamento falhou',
                            detalhes: [
                                'Verifique os dados informados',
                                'Tente novamente em alguns instantes',
                                'Se o problema persistir, contate o suporte'
                            ]
                        }
                    });
                } else if (result.state === 'PROGRESS') {
                    // Atualizar progresso na UI
                    updateProgress(result.status, result.progress);
                }
                // PENDING - continuar polling
            } else {
                // Erro na verificação do status
                clearInterval(pollingInterval);
                displayError({
                    message: result.message || 'Erro ao verificar status',
                    details: {
                        tipo: 'STATUS_ERROR',
                        descricao: 'Não foi possível verificar o progresso',
                        detalhes: [
                            'Tente novamente em alguns instantes',
                            'Se o problema persistir, contate o suporte'
                        ]
                    }
                });
            }
        } catch (error) {
            console.error('Erro no polling:', error);
            
            if (attempts >= maxAttempts) {
                clearInterval(pollingInterval);
                displayError({
                    message: 'Tempo limite excedido',
                    details: {
                        tipo: 'POLLING_TIMEOUT',
                        descricao: 'O processamento demorou muito',
                        detalhes: [
                            'O servidor pode estar sobrecarregado',
                            'Tente novamente em alguns instantes',
                            'Se o problema persistir, aguarde alguns minutos'
                        ]
                    }
                });
            }
        }
    }, 5000); // Polling a cada 5 segundos
}

function updateProgress(status, progress) {
    // Atualizar mensagem de progresso na UI
    const loadingSection = document.getElementById('loadingSection');
    if (loadingSection) {
        const progressElement = loadingSection.querySelector('.progress-message');
        if (progressElement) {
            progressElement.textContent = status || 'Processando...';
        }
        
        const progressBar = loadingSection.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress || 0}%`;
        }
    }
}

function validateCpf(cpf) {
    // Remover caracteres não numéricos
    const cpfClean = cpf.replace(/\D/g, '');
    
    // Validar formato
    if (cpfClean.length !== 11) {
        displayError({
            message: 'CPF inválido',
            details: {
                tipo: 'VALIDATION_ERROR',
                descricao: 'O CPF deve ter 11 dígitos',
                detalhes: [
                    'Digite apenas os números do CPF',
                    'Exemplo: 123.456.789-00',
                    'Verifique se não há espaços ou caracteres especiais'
                ]
            }
        });
        return false;
    }
    
    // Validar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpfClean)) {
        displayError({
            message: 'CPF inválido',
            details: {
                tipo: 'VALIDATION_ERROR',
                descricao: 'CPF com todos os dígitos iguais é inválido',
                detalhes: [
                    'Digite um CPF válido',
                    'Verifique se não há erro de digitação',
                    'Exemplo: 123.456.789-00'
                ]
            }
        });
        return false;
    }
    
    return true;
}

function displaySuccess(result) {
    console.log('Sucesso:', result);
    
    if (elements.successSection) {
        elements.successSection.style.display = 'block';
    }
    
    if (elements.clientInfo) {
        let html = '';
        
        if (result.cliente) {
            html += `<h3>Cliente Encontrado</h3>`;
            html += `<p><strong>Nome:</strong> ${result.cliente.cliente || 'N/A'}</p>`;
            html += `<p><strong>CPF:</strong> ${formatCpf(result.cliente.cpf || '')}</p>`;
        }
        
        if (result.valores) {
            html += `<h3>Valores Calculados</h3>`;
            html += `<p><strong>Receita Total:</strong> ${formatCurrency(result.valores.receita_total || 0)}</p>`;
            html += `<p><strong>Despesas Total:</strong> ${formatCurrency(result.valores.despesas_total || 0)}</p>`;
            html += `<p><strong>Registros Encontrados:</strong> ${result.valores.registros_encontrados || 0}</p>`;
        }
        
        if (result.filename) {
            html += `<h3>PDF Gerado</h3>`;
            html += `<p><strong>Arquivo:</strong> ${result.filename}</p>`;
            html += `<a href="/api/download-pdf/${result.filename}" class="btn btn-primary" download>Download PDF</a>`;
        }
        
        elements.clientInfo.innerHTML = html;
    }
    
    showSection('successSection');
}

function displayError(error) {
    console.error('Erro:', error);
    
    if (elements.errorSection) {
        elements.errorSection.style.display = 'block';
    }
    
    if (elements.errorDetails) {
        let html = `<h3>${error.message}</h3>`;
        
        if (error.details) {
            html += `<p><strong>Tipo:</strong> ${error.details.tipo}</p>`;
            html += `<p><strong>Descrição:</strong> ${error.details.descricao}</p>`;
            
            if (error.details.detalhes && error.details.detalhes.length > 0) {
                html += `<h4>Soluções:</h4><ul>`;
                error.details.detalhes.forEach(detalhe => {
                    html += `<li>${detalhe}</li>`;
                });
                html += `</ul>`;
            }
        }
        
        elements.errorDetails.innerHTML = html;
    }
    
    showSection('errorSection');
}

function setLoading(loading) {
    isLoading = loading;
    
    if (elements.generateBtn) {
        elements.generateBtn.disabled = loading;
        elements.generateBtn.textContent = loading ? 'Processando...' : 'Gerar PDF';
    }
    
    if (loading) {
        // Limpar polling anterior
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        currentTaskId = null;
    }
}

function showSection(sectionId) {
    // Esconder todas as seções
    const sections = ['loadingSection', 'successSection', 'errorSection'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Mostrar a seção especificada
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
}

function resetForm() {
    // Limpar polling
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
    currentTaskId = null;
    
    // Resetar formulário
    if (elements.cpfInput) {
        elements.cpfInput.value = '';
        elements.cpfInput.focus();
    }
    
    // Esconder todas as seções
    showSection('loadingSection');
    
    setLoading(false);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value || 0);
}

function formatCpf(cpf) {
    if (!cpf) return '';
    const clean = cpf.replace(/\D/g, '');
    return clean.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}