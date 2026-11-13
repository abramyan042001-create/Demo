const assert = require("node:assert/strict"); // Используем встроенные строгие проверки Node.js без сторонних пакетов.
const fs = require("node:fs"); // Читаем настоящий JavaScript приложения, чтобы не тестировать его переписанную копию.
const path = require("node:path"); // Собираем путь к скрипту относительно каталога этого теста.
const vm = require("node:vm"); // Выполняем браузерный скрипт в изолированном контексте с минимальным DOM-макетом.
const events = {}; // Здесь сохраняем обработчики мыши, клавиатуры и фокуса карусели.
const buttons = { next: {}, prev: {} }; // Два объекта заменяют только кнопки управления слайдером.
for (const button of Object.values(buttons)) button.addEventListener = (name, callback) => { button[name] = callback; }; // Регистрация события сохраняет функцию для последующего вызова тестом.
const slides = Array.from({ length: 4 }, () => ({ active: false, hidden: null })); // Ровно четыре объекта представляют четыре кадра приложения.
for (const slide of slides) { // Придаём каждому кадру только те методы DOM, которыми пользуется app.js.
    slide.classList = { toggle(name, value) { slide.active = value; } }; // toggle фиксирует, выбран ли данный кадр.
    slide.setAttribute = (name, value) => { slide.hidden = value; }; // aria-hidden записывается для проверки доступности.
} // Завершаем подготовку четырёх кадров.
const counter = { textContent: "" }; // Текстовый объект заменяет счётчик вида 1 / 4.
const reducedMotion = { matches: false, addEventListener() {} }; // По умолчанию движение разрешено; значение можно изменить из теста.
let interval = null; // Храним функцию интервала вместо настоящего ожидания трёх секунд.
let intervalDelay = null; // Отдельно фиксируем запрошенную скриптом задержку.
const slider = { querySelectorAll: () => slides, querySelector: (selector) => selector === ".slide-counter" ? counter : buttons[selector.slice(1)], matches: () => false, addEventListener: (name, callback) => { events[name] = callback; } }; // Минимальный контейнер предоставляет поиск элементов и регистрацию событий.
const submitButton = { disabled: false }; // Макет кнопки отправки формы нужен для проверки loader-поведения.
const loader = { hidden: true }; // Индикатор изначально скрыт, как в HTML-шаблоне.
let submit = null; // Здесь будет обработчик события submit.
const form = { querySelector: (selector) => selector === ".loading-message" ? loader : submitButton, addEventListener: (name, callback) => { submit = callback; } }; // Форма возвращает только свои кнопку и индикатор.
const pageEvents = {}; // Сохраняем обработчики событий окна браузера.
const document = { hidden: false, querySelectorAll: (selector) => selector === ".slider" ? [slider] : selector === "form[data-loading]" ? [form] : selector === ".loading-message" ? [loader] : [submitButton], addEventListener() {} }; // DOM-макет не проверяет вёрстку: только функции и состояния JavaScript.
const window = { matchMedia: () => reducedMotion, clearInterval: () => { interval = null; }, setInterval: (callback, delay) => { interval = callback; intervalDelay = delay; return 1; }, setTimeout: (callback) => callback(), addEventListener: (name, callback) => { pageEvents[name] = callback; } }; // Таймеры исполняются вручную, поэтому тест быстрый и воспроизводимый.
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../static/js/app.js"), "utf8"), { document, window }); // Загружаем и запускаем рабочий код в подготовленной среде.
assert.equal(counter.textContent, "1 / 4"); // Первоначально должен отображаться первый кадр.
assert.equal(intervalDelay, 3000); // Автосмена обязана использовать интервал 3000 мс из задания.
buttons.prev.click(); // Нажимаем «назад» на первом кадре.
assert.equal(counter.textContent, "4 / 4"); // Циклический переход должен попасть на четвёртый кадр.
buttons.next.click(); // Нажимаем «вперёд» на последнем кадре.
assert.equal(counter.textContent, "1 / 4"); // Следующим снова становится первый кадр.
interval(); // Вручную исполняем один шаг автосмены без реального ожидания.
assert.equal(counter.textContent, "2 / 4"); // Таймер должен продвинуть слайдер на один кадр.
assert.equal(slides.filter((slide) => slide.active).length, 1); // В любой момент активен только один из четырёх кадров.
assert.equal(slides[1].hidden, "false"); // Активный кадр доступен экранному диктору.
assert.equal(slides[0].hidden, "true"); // Неактивный кадр скрыт из дерева доступности.
events.mouseenter(); // Пользователь наводит мышь на карусель.
assert.equal(interval, null); // Во время взаимодействия автосмена приостанавливается.
events.mouseleave(); // Пользователь убирает мышь.
assert.equal(typeof interval, "function"); // Автосмена возобновляется после ухода указателя.
reducedMotion.matches = true; // Моделируем включённое в ОС ограничение движения.
events.mouseleave(); // Пробуем повторно запустить интервал.
assert.equal(interval, null); // Системная настройка должна удерживать слайдер на паузе.
submit(); // Моделируем отправку валидной формы.
assert.equal(submitButton.disabled, true); // Пока запрос отправляется, повторный клик заблокирован.
assert.equal(loader.hidden, false); // Пользователь видит индикатор отправки.
pageEvents.pageshow(); // Моделируем возврат назад через браузерный cache.
assert.equal(submitButton.disabled, false); // Восстановленная страница снова допускает отправку формы.
assert.equal(loader.hidden, true); // Старый индикатор не остаётся видимым после возврата.
console.log("PASS: 4 слайда, переходы по кругу, 3000 мс, доступность, пауза, отправка формы."); // Отчёт описывает покрытые проверки без утверждения о визуальной проверке браузером.
