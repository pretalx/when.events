if (window.location.hash) {
    const selected = document.querySelector(window.location.hash + ' input');
    if (selected) {
        selected.checked = true;
    }
}
