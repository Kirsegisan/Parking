document.addEventListener('DOMContentLoaded', () => {
    // Функция для скрытия слогана при прокрутке
    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            document.body.classList.add('scrolled');
        } else {
            document.body.classList.remove('scrolled');
        }
    });

    // Открытие и закрытие меню
    const menuButton = document.querySelector('.menu-button');
    const menuList = document.querySelector('.menu-list');

    menuButton.addEventListener('click', () => {
        document.body.classList.toggle('menu-opened');
    });
});
