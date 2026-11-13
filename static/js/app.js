const slides = document.querySelectorAll(".slide"); // Находим все кадры: на странице входа их четыре, на других страницах может быть ноль.
let index = 0; // Запоминаем номер текущего кадра; JavaScript считает с нуля.
function showSlide(number) { // Эта функция показывает кадр с переданным номером.
    index = (number + slides.length) % slides.length; // Остаток от деления замыкает цикл: после четвёртого снова первый, до первого — четвёртый.
    slides.forEach((slide, position) => { // Проверяем по очереди каждый кадр и его номер.
        slide.classList.toggle("active", position === index); // Добавляем active только выбранному кадру; CSS сделает его видимым.
        slide.setAttribute("aria-hidden", position !== index); // Неактивные изображения не должны читаться экранным диктором.
    }); // Заканчиваем перебор кадров.
} // Заканчиваем функцию переключения.
if (slides.length > 0) { // Не подключаем кнопки слайдера там, где самого слайдера нет.
    document.getElementById("next").onclick = () => showSlide(index + 1); // Нажатие правой стрелки показывает следующий кадр.
    document.getElementById("prev").onclick = () => showSlide(index - 1); // Нажатие левой стрелки показывает предыдущий кадр.
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) { // Учитываем желание пользователя отключить автоматические движения.
        setInterval(() => showSlide(index + 1), 3000); // Каждые 3000 миллисекунд, то есть три секунды, выполняем один шаг вперёд.
    } // Заканчиваем проверку настройки движения.
} // Заканчиваем настройку слайдера.
document.querySelectorAll(".saving-form").forEach((form) => { // Находим формы, для которых нужен индикатор отправки.
    const button = form.querySelector('button[type="submit"]'); // Получаем кнопку именно этой формы, а не первую кнопку страницы.
    const text = button.textContent; // Запоминаем исходную надпись, чтобы восстановить её после возврата назад.
    form.onsubmit = () => { button.disabled = true; button.textContent = "Сохраняем…"; }; // На время отправки показываем ожидание и блокируем повторное нажатие.
    window.addEventListener("pageshow", () => { button.disabled = false; button.textContent = text; }); // После возврата браузером кнопка снова работает и имеет прежнюю надпись.
}); // Заканчиваем настройку всех форм.
