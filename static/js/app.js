"use strict"; // Строгий режим запрещает некоторые неявные ошибки, например случайное создание глобальной переменной.
document.querySelectorAll(".slider").forEach((slider) => { // Независимо подключаем управление к каждой карусели на странице.
    const slides = [...slider.querySelectorAll(".slide")]; // Превращаем найденные кадры в массив, чтобы использовать длину и перебор.
    const counter = slider.querySelector(".slide-counter"); // Сохраняем ссылку на текстовый счётчик, чтобы не искать его при каждой смене.
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)"); // Проверяем системное пожелание ограничить анимации.
    let index = 0; // Переменная хранит индекс текущего кадра; нумерация массива начинается с нуля.
    let timer = null; // Здесь будет id интервала; null означает, что автопереключение остановлено.
    function show(nextIndex) { // Функция показывает один кадр по переданному номеру.
        index = (nextIndex + slides.length) % slides.length; // Остаток от деления замыкает переходы; прибавление длины обрабатывает шаг назад с нуля.
        slides.forEach((slide, position) => { // Проходим по всем четырём кадрам и сравниваем их индекс с выбранным.
            const active = position === index; // Получаем true ровно для одного активного кадра.
            slide.classList.toggle("active", active); // Добавляем CSS-класс выбранному кадру и убираем его у остальных.
            slide.setAttribute("aria-hidden", String(!active)); // Неактивные иллюстрации не должны читаться экранным диктором.
        }); // Завершаем обновление состояний всех кадров.
        counter.textContent = `${index + 1} / ${slides.length}`; // Для человека считаем с единицы и показываем общее число кадров.
    } // Завершаем функцию смены кадра.
    function stop() { // Отдельная функция отвечает за остановку автопереключения.
        window.clearInterval(timer); // Удаляем интервал, если он существовал; null безопасен.
        timer = null; // Помечаем, что работающего таймера больше нет.
    } // Завершаем функцию остановки.
    function start() { // Запускаем интервал только когда это уместно.
        stop(); // Убираем предыдущий таймер, чтобы повторные события не ускоряли слайдер.
        if (document.hidden || reducedMotion.matches || slider.matches(":hover, :focus-within")) return; // Пауза в фоновой вкладке, при ограничении движения и во время взаимодействия.
        timer = window.setInterval(() => show(index + 1), 3000); // Обычный автоматический переход происходит ровно раз в 3000 миллисекунд.
    } // Завершаем функцию запуска интервала.
    slider.querySelector(".next").addEventListener("click", () => show(index + 1)); // Правая стрелка показывает следующий кадр с циклическим возвратом.
    slider.querySelector(".prev").addEventListener("click", () => show(index - 1)); // Левая стрелка показывает предыдущий кадр.
    slider.addEventListener("keydown", (event) => { // Поддерживаем навигацию без мыши, когда фокус находится в карусели.
        if (event.key === "ArrowRight") { event.preventDefault(); show(index + 1); } // Правая клавиша меняет кадр и не прокручивает страницу.
        if (event.key === "ArrowLeft") { event.preventDefault(); show(index - 1); } // Левая клавиша делает шаг назад.
    }); // Завершаем обработчик клавиатуры.
    slider.addEventListener("mouseenter", stop); // Даём спокойно рассмотреть кадр при наведении указателя.
    slider.addEventListener("mouseleave", start); // После ухода указателя возобновляем обычный режим.
    slider.addEventListener("focusin", stop); // Фокус пользователя клавиатуры также ставит карусель на паузу.
    slider.addEventListener("focusout", () => window.setTimeout(start, 0)); // Проверяем уход фокуса после того, как браузер назначит новый активный элемент.
    document.addEventListener("visibilitychange", start); // Уход в другую вкладку останавливает интервал; возвращение запускает заново.
    reducedMotion.addEventListener("change", start); // Изменение настройки движения учитывается без перезагрузки страницы.
    show(0); // Явно устанавливаем первый кадр и правильное состояние доступности при старте.
    start(); // Включаем автоматическую смену кадров, если нет причин для паузы.
}); // Завершаем настройку всех слайдеров.
document.querySelectorAll("form[data-loading]").forEach((form) => { // Находим формы, которым нужен индикатор отправки.
    form.addEventListener("submit", () => { // submit возникает после успешной встроенной браузерной валидации.
        const button = form.querySelector('button[type="submit"]'); // Находим основную кнопку текущей формы.
        const loader = form.querySelector(".loading-message"); // Находим текстовый индикатор в пределах этой же формы.
        if (button) button.disabled = true; // Не допускаем повторные клики, пока отправляется запрос.
        if (loader) loader.hidden = false; // Показываем ожидание; без JavaScript форма всё равно отправляется обычным способом.
    }); // Завершаем обработчик отправки.
}); // Завершаем перебор форм.
window.addEventListener("pageshow", () => { // Браузер может восстановить старую страницу из back-forward cache.
    document.querySelectorAll('form[data-loading] button[type="submit"]').forEach((button) => { button.disabled = false; }); // Снова разрешаем отправку формы после возвращения кнопкой «Назад».
    document.querySelectorAll(".loading-message").forEach((loader) => { loader.hidden = true; }); // Скрываем устаревшие индикаторы отправки при восстановлении страницы.
}); // Завершаем обработчик восстановления страницы.
