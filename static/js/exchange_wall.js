// 交换墙页面交互

document.addEventListener('DOMContentLoaded', function() {
    // 可以添加筛选、排序等功能
    console.log('El Mural del Trueque cargado');
    
    // 可以添加动画效果
    const exchangeCards = document.querySelectorAll('.exchange-card');
    exchangeCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

