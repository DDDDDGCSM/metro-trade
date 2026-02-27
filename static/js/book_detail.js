// 书籍详情页交互

// 标签页切换
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // 移除所有活动状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 添加活动状态
            this.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
        });
    });
});

// 模态框控制
function openExchangeModal() {
    const modal = document.getElementById('exchangeModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeExchangeModal() {
    const modal = document.getElementById('exchangeModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    
    // 重置到第一步
    const steps = document.querySelectorAll('.modal-step');
    steps.forEach((step, index) => {
        step.classList.remove('active');
        if (index === 0) {
            step.classList.add('active');
        }
    });
    
    // 重置表单
    document.getElementById('userStory').value = '';
    const selectedBooks = document.querySelectorAll('.book-option.selected');
    selectedBooks.forEach(book => book.classList.remove('selected'));
}

// 步骤导航
function nextStep(stepNumber) {
    const currentStep = document.querySelector('.modal-step.active');
    const nextStep = document.getElementById(`step${stepNumber}`);
    
    if (stepNumber === 2) {
        // 验证第一步
        const story = document.getElementById('userStory').value.trim();
        if (story.length < 50) {
            alert('Por favor, escribe al menos 50 palabras en tu historia.');
            return;
        }
    }
    
    currentStep.classList.remove('active');
    nextStep.classList.add('active');
    
    // 更新步骤指示器
    updateStepIndicator(stepNumber);
}

function prevStep(stepNumber) {
    const currentStep = document.querySelector('.modal-step.active');
    const prevStep = document.getElementById(`step${stepNumber}`);
    
    currentStep.classList.remove('active');
    prevStep.classList.add('active');
    
    updateStepIndicator(stepNumber);
}

function updateStepIndicator(activeStep) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        if (index + 1 < activeStep) {
            step.classList.add('completed');
            step.innerHTML = '<span>✓</span>';
        } else if (index + 1 === activeStep) {
            step.classList.add('active');
            step.innerHTML = `<span>${activeStep}</span>`;
        } else {
            step.innerHTML = `<span>${index + 1}</span>`;
        }
    });
}

// 选择图书
function selectBook(element) {
    // 移除其他选中状态
    document.querySelectorAll('.book-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // 添加选中状态
    element.classList.add('selected');
}

// 提交交换申请
function submitExchange() {
    const story = document.getElementById('userStory').value.trim();
    const selectedBook = document.querySelector('.book-option.selected');
    
    if (!story || story.length < 50) {
        alert('Por favor, completa tu historia (mínimo 50 palabras).');
        return;
    }
    
    if (!selectedBook) {
        alert('Por favor, selecciona un libro para intercambiar.');
        return;
    }
    
    // 发送请求到后端
    fetch('/api/exchange/request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story: story,
            selected_book: selectedBook.querySelector('p').textContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('¡Solicitud enviada exitosamente! Te notificaremos cuando el usuario responda.');
            closeExchangeModal();
        } else {
            alert('Error al enviar la solicitud. Por favor, intenta de nuevo.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al enviar la solicitud. Por favor, intenta de nuevo.');
    });
}

// 点击模态框外部关闭
document.addEventListener('click', function(event) {
    const modal = document.getElementById('exchangeModal');
    if (event.target === modal) {
        closeExchangeModal();
    }
});

// ESC键关闭模态框
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeExchangeModal();
    }
});

