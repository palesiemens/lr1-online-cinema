const cards = [...document.querySelectorAll('.movie-card')];
const filters = [...document.querySelectorAll('.filter')];
const searchInput = document.querySelector('#search');
const emptyState = document.querySelector('#empty-state');
const dialog = document.querySelector('#movie-dialog');
const dialogTitle = document.querySelector('#dialog-title');
const dialogDescription = document.querySelector('#dialog-description');
let selectedGenre = 'all';

function applyFilters() {
  const query = searchInput.value.trim().toLocaleLowerCase('ru');
  let visible = 0;
  cards.forEach((card) => {
    const matchesGenre = selectedGenre === 'all' || card.dataset.genre.split(' ').includes(selectedGenre);
    const haystack = `${card.dataset.title} ${card.dataset.description} ${card.dataset.genre}`.toLocaleLowerCase('ru');
    const matchesQuery = !query || haystack.includes(query);
    const show = matchesGenre && matchesQuery;
    card.hidden = !show;
    if (show) visible += 1;
  });
  emptyState.hidden = visible !== 0;
}

filters.forEach((button) => {
  button.addEventListener('click', () => {
    filters.forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    selectedGenre = button.dataset.filter;
    applyFilters();
  });
});
searchInput.addEventListener('input', applyFilters);

document.querySelectorAll('[data-details]').forEach((button) => {
  button.addEventListener('click', () => {
    const movieName = button.dataset.details;
    const card = cards.find((item) => item.dataset.title === movieName);
    dialogTitle.textContent = movieName;
    dialogDescription.textContent = card?.dataset.description || 'Описание фильма появится после загрузки карточки из каталога.';
    dialog.showModal();
  });
});

document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
document.querySelector('#dialog-watch').addEventListener('click', () => {
  document.querySelector('#dialog-watch').textContent = '▶ Добавлено в историю (демо)';
});
document.querySelector('#dialog-favorite').addEventListener('click', (event) => {
  event.currentTarget.textContent = '♥ В избранном (демо)';
});
