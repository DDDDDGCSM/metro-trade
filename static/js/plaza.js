// 图书广场页面交互

document.addEventListener('DOMContentLoaded', function() {
    // 过滤器功能
    const filterButtons = document.querySelectorAll('.filter-btn');
    const bookCards = document.querySelectorAll('.book-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 更新活动状态
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            filterBooks(filter);
        });
    });
    
    function filterBooks(filter) {
        let visibleCount = 0;
        
        bookCards.forEach(card => {
            const bookId = card.getAttribute('data-book-id');
            let show = true;
            
            if (filter === 'has_story') {
                // 这里应该从数据中检查，暂时显示所有
                show = true;
            } else if (filter === 'verified') {
                // 这里应该从数据中检查，暂时显示所有
                show = true;
            } else if (filter !== 'all') {
                // 其他分类过滤
                show = true;
            }
            
            if (show) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // 显示/隐藏空状态
        const emptyState = document.getElementById('emptyState');
        if (visibleCount === 0) {
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
        }
    }
    
    // 轮播功能（简单实现）
    const carousel = document.querySelector('.story-carousel');
    if (carousel) {
        let scrollPosition = 0;
        const scrollAmount = 320;
        
        // 可以添加左右箭头按钮
        // 这里只是基础实现
    }
});

