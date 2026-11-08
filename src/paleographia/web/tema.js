// Tema do PaleographIA: "auto" segue o sistema; "noturno" e "claro" fixam a escolha.
// Carregado no <head> antes do CSS, para a página já abrir no tema certo, sem piscar.
// Qualquer botão com id "themeToggle" alterna entre automático, noturno e claro.
(() => {
  const KEY = 'paleographia.tema', ORDER = ['auto', 'noturno', 'claro'];
  const LABEL = {auto: 'automático', noturno: 'noturno', claro: 'claro'};
  const media = matchMedia('(prefers-color-scheme: dark)');
  let choice = 'auto';
  try { choice = localStorage.getItem(KEY) || 'auto'; } catch { /* armazenamento opcional */ }
  if (!ORDER.includes(choice)) choice = 'auto';
  function apply() {
    const dark = choice === 'noturno' || (choice === 'auto' && media.matches);
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    const button = document.getElementById('themeToggle');
    if (button) button.textContent = `Tema: ${LABEL[choice]}`;
  }
  apply();
  media.addEventListener('change', apply);
  document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('themeToggle');
    if (!button) return;
    button.title = 'Alterna entre automático (segue o sistema), noturno e claro';
    button.addEventListener('click', () => {
      choice = ORDER[(ORDER.indexOf(choice) + 1) % ORDER.length];
      try { localStorage.setItem(KEY, choice); } catch { /* armazenamento opcional */ }
      apply();
    });
    apply();
  });
})();
