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
            signal: AbortSignal.timeout(120000) // 2 minutos de timeout para produção
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
                 // Se a resposta estiver vazia, tratar como erro de servidor
                 if (!responseText || responseText.trim() === '') {
                     console.error('Response vazia - Status:', response.status);
                     
                     if (response.status === 502) {
                         displayError({
                             message: 'Servidor temporariamente indisponível',
                             details: {
                                 tipo: 'BAD_GATEWAY',
                                 descricao: 'O servidor está temporariamente indisponível',
                                 detalhes: [
                                     'O servidor pode estar reiniciando',
                                     'Tente novamente em alguns instantes',
                                     'Se o problema persistir, aguarde alguns minutos'
                                 ]
                             }
                         });
                     } else {
                         displayError({
                             message: 'Erro interno do servidor',
                             details: {
                                 tipo: 'ERRO_SERVIDOR',
                                 descricao: 'O servidor retornou uma resposta vazia',
                                 detalhes: [
                                     'O servidor pode estar temporariamente indisponível',
                                     'Tente novamente em alguns instantes',
                                     'Se o problema persistir, entre em contato com o suporte'
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
                 
                 // Se não conseguir parsear JSON, provavelmente é um erro HTML
                 displayError({
                     message: 'Erro interno do servidor',
                     details: {
                         tipo: 'ERRO_SERVIDOR',
                         descricao: 'O servidor retornou uma resposta inválida',
                         detalhes: [
                             'O servidor pode estar temporariamente indisponível',
                             'Tente novamente em alguns instantes',
                             'Se o problema persistir, entre em contato com o suporte'
                         ]
                     }
                 });
                 return;
             }
        } catch (error) {
            console.error('Erro ao ler response:', error);
            displayError({
                message: 'Erro de conexão',
                details: {
                    tipo: 'ERRO_CONEXAO',
                    descricao: 'Não foi possível ler a resposta do servidor',
                    detalhes: [
                        'Verifique sua conexão com a internet',
                        'O servidor pode estar temporariamente indisponível',
                        'Tente novamente em alguns instantes'
                    ]
                }
            });
            return;
        }
        
        if (response.ok && result.success) {
            // Download do PDF
            if (result.filename) {
                const downloadUrl = `${API_BASE}/download-pdf/${result.filename}`;
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
            
            // Mostrar sucesso
            displaySuccess(result);
            
        } else {
            // Mostrar erro
            if (response.status === 404) {
                displayError({
                    message: 'Cliente não encontrado',
                    details: {
                        tipo: 'CLIENTE_NAO_ENCONTRADO',
                        descricao: 'O CPF informado não foi encontrado na base de dados',
                        detalhes: [
                            'Verifique se o CPF está correto',
                            'Certifique-se de que o cliente está cadastrado no sistema'
                        ]
                    }
                });
            } else if (response.status === 500) {
                displayError({
                    message: 'Erro interno do servidor',
                    details: {
                        tipo: 'ERRO_SERVIDOR',
                        descricao: 'Ocorreu um erro interno no servidor',
                        detalhes: [
                            'O servidor pode estar temporariamente indisponível',
                            'Tente novamente em alguns instantes',
                            'Se o problema persistir, entre em contato com o suporte'
                        ]
                    }
                });
            } else {
                displayError(result);
            }
        }
        
    } catch (error) {
        console.error('Erro na requisição:', error);
        
        // Determinar o tipo de erro específico
        let errorMessage = 'Erro de conexão';
        let errorDetails = {
            tipo: 'ERRO_CONEXAO',
            descricao: 'Não foi possível conectar com o servidor',
            detalhes: [
                'Verifique sua conexão com a internet',
                'Certifique-se de que o servidor está funcionando',
                'Tente novamente em alguns instantes'
            ]
        };
        
        // Se for um erro de rede específico
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = 'Servidor não disponível';
            errorDetails.descricao = 'O servidor não está respondendo';
            errorDetails.detalhes = [
                'O servidor pode estar temporariamente indisponível',
                'Verifique se a URL está correta',
                'Tente novamente em alguns instantes'
            ];
        }
        
        displayError({
            message: errorMessage,
            details: errorDetails
        });
    }
    
    setLoading(false);
}

function validateCpf(cpf) {
    if (!cpf) return false;
    
    const cpfClean = cpf.replace(/\D/g, '');
    
    if (cpfClean.length !== 11) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpfClean)) return false;
    
    // Validar dígitos verificadores
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpfClean[i]) * (10 - i);
    }
    let digit1 = (sum * 10) % 11;
    if (digit1 === 10) digit1 = 0;
    
    if (digit1 !== parseInt(cpfClean[9])) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpfClean[i]) * (11 - i);
    }
    let digit2 = (sum * 10) % 11;
    if (digit2 === 10) digit2 = 0;
    
    return digit2 === parseInt(cpfClean[10]);
}

function displaySuccess(result) {
    let html = '';
    
    if (result.cliente) {
        html += `
            <p><strong>Cliente:</strong> ${result.cliente.cliente}</p>
            <p><strong>CPF:</strong> ${formatCpf(result.cliente.cpf)}</p>
        `;
        
        if (result.cliente.empreendimento) {
            html += `<p><strong>Empreendimento:</strong> ${result.cliente.empreendimento}</p>`;
        }
    }
    
    if (result.valores) {
        html += `
            <p><strong>Receita Total:</strong> R$ ${formatCurrency(result.valores.receita_total)}</p>
            <p><strong>Despesas:</strong> R$ ${formatCurrency(result.valores.despesas_total)}</p>
        `;
        
        if (result.valores.registros_encontrados) {
            html += `<p><strong>Registros:</strong> ${result.valores.registros_encontrados}</p>`;
        }
    }
    
    if (result.filename) {
        html += `<p><strong>Arquivo:</strong> ${result.filename}</p>`;
    }
    
    elements.clientInfo.innerHTML = html;
    showSection('successSection');
}

function displayError(error) {
    let html = '<h4>Detalhes do Erro</h4>';
    
    if (error.message) {
        html += `<p><strong>Mensagem:</strong> ${error.message}</p>`;
    }
    
    // Tratar diferentes tipos de erro
    if (error.erro_consistencia) {
        const erro = error.erro_consistencia;
        html += `<p><strong>Tipo:</strong> ${erro.tipo}</p>`;
        html += `<p><strong>Descrição:</strong> ${erro.descricao}</p>`;
        
        if (erro.tipo === 'SEM_DADOS_FINANCEIROS') {
            if (erro.detalhes && erro.detalhes.length > 0) {
                html += '<p><strong>Detalhes:</strong></p><ul>';
                erro.detalhes.forEach(detalhe => {
                    html += `<li>${detalhe}</li>`;
                });
                html += '</ul>';
            }
        } else if (erro.tipo === 'DIFERENCA_SALDOS') {
            html += `<p><strong>Diferença:</strong> R$ ${formatCurrency(erro.diferenca)}</p>`;
            html += `<p><strong>Saldo Union:</strong> R$ ${formatCurrency(erro.saldo_union)}</p>`;
            html += `<p><strong>Saldo Paggo:</strong> R$ ${formatCurrency(erro.saldo_paggo)}</p>`;
        }
    } else if (error.details) {
        const details = error.details;
        if (details.descricao) {
            html += `<p><strong>Descrição:</strong> ${details.descricao}</p>`;
        }
        if (details.detalhes && details.detalhes.length > 0) {
            html += '<p><strong>Soluções:</strong></p><ul>';
            details.detalhes.forEach(detalhe => {
                html += `<li>${detalhe}</li>`;
            });
            html += '</ul>';
        }
    }
    
    elements.errorDetails.innerHTML = html;
    showSection('errorSection');
}

function setLoading(loading) {
    isLoading = loading;
    elements.generateBtn.disabled = loading;
    
    if (loading) {
        elements.generateBtn.innerHTML = `
            <div class="spinner" style="width: 20px; height: 20px; margin: 0;"></div>
            <span>Processando...</span>
        `;
    } else {
        elements.generateBtn.innerHTML = `
            <i class="fas fa-file-pdf"></i>
            <span>Gerar Declaração</span>
        `;
    }
}

function showSection(sectionId) {
    ['loadingSection', 'successSection', 'errorSection'].forEach(id => {
        if (elements[id]) {
            elements[id].classList.add('hidden');
        }
    });
    
    if (elements[sectionId]) {
        elements[sectionId].classList.remove('hidden');
    }
}

function resetForm() {
    elements.cpfInput.value = '';
        elements.cpfInput.focus();
    showSection('');
    setLoading(false);
}



function formatCurrency(value) {
    if (!value || isNaN(value)) return '0,00';
    return parseFloat(value).toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
}

function formatCpf(cpf) {
    if (!cpf) return '';
    const clean = cpf.replace(/\D/g, '');
    return clean.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}