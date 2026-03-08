/**
 * Функция для сворачивания/разворачивания аккордеона
 * @param {HTMLElement} button - нажатая кнопка
 */
function toggleAccordion(button) {
    const item = button.parentElement;
    const isActive = item.classList.contains('active');

    // Опционально: закрывать все остальные
    // const allItems = document.querySelectorAll('.accordion-item');
    // allItems.forEach(i => i.classList.remove('active'));

    // Переключаем текущий
    if (isActive) {
        item.classList.remove('active');
    } else {
        item.classList.add('active');
    }
}

/**
 * Авто-разворачивание первого элемента (опционально)
 */
document.addEventListener('DOMContentLoaded', function() {
    const firstItem = document.querySelector('.accordion-item');
    if (firstItem) {
        firstItem.classList.add('active');
    }

    // Поиск по содержимому (Ctrl+F аналог)
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            const searchTerm = prompt('Введите текст для поиска:');
            if (searchTerm) {
                searchInHelp(searchTerm);
            }
        }
    });
});

/**
 * Поиск по содержимому помощи
 */
function searchInHelp(term) {
    const items = document.querySelectorAll('.accordion-item');
    let found = 0;

    items.forEach(item => {
        const content = item.textContent.toLowerCase();
        if (content.includes(term.toLowerCase())) {
            item.classList.add('active');
            item.style.borderColor = '#4CAF50';
            setTimeout(() => {
                item.style.borderColor = '';
            }, 2000);
            found++;
        }
    });

    if (found === 0) {
        alert('Ничего не найдено');
    } else {
        console.log(`Найдено: ${found} секций`);
    }
}

/**
 * Развернуть все секции
 */
function expandAll() {
    document.querySelectorAll('.accordion-item').forEach(item => {
        item.classList.add('active');
    });
}

/**
 * Свернуть все секции
 */
function collapseAll() {
    document.querySelectorAll('.accordion-item').forEach(item => {
        item.classList.remove('active');
    });
}

// Добавляем кнопки управления (можно вызвать из консоли)
console.log('💡 Доступные функции:');
console.log('  expandAll() — развернуть все');
console.log('  collapseAll() — свернуть все');
console.log('  searchInHelp("текст") — поиск');