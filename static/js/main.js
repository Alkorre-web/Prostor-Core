// Современный подход (не onclick в HTML!)
document.getElementById('myButton').addEventListener('click', function() {
    alert('Кнопка нажата!');
});

// onMouseOver аналог
document.getElementById('myButton').addEventListener('mouseover', function() {
    console.log('Мышь на кнопке!');
});